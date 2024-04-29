import os
import ssl
import nltk
import time
import uuid
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from threading import Thread, Lock
from queue import Queue
from crawler import abort_search_event, breadth_first_search, bidirectional_search, a_star
import logging
from threading import Thread, Event, Timer
from crawler import precompute_finish_page_keywords

class StoppableThread(Thread):
    def __init__(self, timeout=None, *args, **kwargs):
        # Remove the custom 'timeout' argument before calling the superclass constructor
        self._timeout = timeout
        kwargs.pop('timeout', None)  # Remove timeout from kwargs if it exists to prevent TypeError
        super().__init__(*args, **kwargs)
        self._stop_event = Event()
        self._start_time = None

    def run(self):
        if self._timeout:
            # Setup a timer that will stop the thread after the timeout period
            timer = Timer(self._timeout, self.stop)
            timer.start()
        try:
            super().run()
        finally:
            if self._timeout:
                timer.cancel()  # Cancel the timer if the work completes before the timeout

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

logging.basicConfig(level=logging.INFO)  # Configure the logging level

# Add a global dictionary to keep track of search states
search_states = {}
search_completed = {}

# Set PYTHONHTTPSVERIFY environment variable to disable SSL certificate verification
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Set NLTK_DATA environment variable
nltk_data_path = "/Users/tony/nltk_data"
os.environ["NLTK_DATA"] = nltk_data_path
nltk.data.path.append(nltk_data_path)

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Set the rate limit for requests
RATE_LIMIT = "10/minute"

# Initialize the Flask application
app = Flask(__name__, static_folder='../client')

# Set the rate limit storage explicitly for Flask-Limiter
storage_uri = "memory://"

# Initialize Flask-Limiter with explicit storage URI
limiter = Limiter(app=app, key_func=get_remote_address, storage_uri=storage_uri)

# Initialize a queue and lock for managing logs and search results
logs_queue = Queue()  # Thread-safe queue for logs
search_results = {}
search_results_lock = Lock()  # Lock for thread-safe access to search_results

@app.route('/', methods=['GET'])
def home():
    # Serve 'index.html' from the static_folder
    return send_from_directory(app.static_folder, 'index.html')


def search_and_log(start_page, finish_page, search_method, search_id):
    global search_completed, search_states
    search_states[search_id] = {'completed': False}
    # Precompute and cache the finish page keywords
    if search_method == 'a_star':  # Do this only if A* search is selected
        precompute_finish_page_keywords(finish_page)

    print(f"Search and log called with search_id: {search_id}")  # Confirm the search_id
    path = None
    discovered = 0
    total_links = 0  # To keep the total number of links found
    error_message = None
    start_time = time.time()

    # Initialize the search as incomplete
    search_completed[search_id] = False

    try:
        abort_search_event.clear()

        if search_method == 'a_star':
            path, time_elapsed, discovered, search_method, total_links = a_star(start_page, finish_page, logs_queue, search_id)
        elif search_method == 'bidirectional':
            path, time_elapsed, discovered, search_method, total_links = bidirectional_search(start_page, finish_page, logs_queue, search_id)
        elif search_method == 'breadth-first':
            path, time_elapsed, discovered, search_method, total_links = breadth_first_search(start_page, finish_page, logs_queue, search_id)
        
        print(f"Search {search_id} completed. Path found: {path}")

        if path:
            # If a path is found, set the search state to completed
            search_states[search_id]['completed'] = True
            logs_queue.put(f"Search {search_id} completed. Path found: {path}")
        else:
            logs_queue.put(f"Search {search_id} concluded without finding a path.")

    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logs_queue.put(f"Search {search_id} error: {error_message}")
        print(f"Search {search_id} failed with error: {error_message}")
        time_elapsed = time.time() - start_time

    finally:  # Ensure the following code runs regardless of exceptions
        search_time = time.time() - start_time
        path_length = len(path) if path else 0

        with search_results_lock:
            search_results[search_id] = {
                'path': path,
                'time': search_time,
                'discovered': discovered,
                'total_links': total_links,
                'completed': path is not None,
                'error': error_message,
                'search_method': search_method,
                'path_length': path_length,
            }
            print(f"Stored results for {search_id}: {search_results[search_id]}")
        
        # Mark the search as completed
        search_completed[search_id] = True

        if error_message:
            error_completion_message = f"Search {search_id} error: {error_message}"
            print(error_completion_message)
            logs_queue.put(error_completion_message)
        else:
            print(f"Search {search_id} completed successfully.")

        time.sleep(1)  # Sleep to ensure clean thread shutdown


@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.get_json()
    start_page = data.get('start')
    finish_page = data.get('finish')
    search_method = data.get('method', 'breadth-first')
    timeout = 300  # Example: 300 seconds timeout

    if not start_page or not finish_page:
        return jsonify({'message': 'Missing parameters'}), 400

    search_id = str(uuid.uuid4())
    search_thread = StoppableThread(target=search_and_log, args=(start_page, finish_page, search_method, search_id), timeout=300)
    search_thread.start()

    return jsonify({'message': 'Search started', 'search_id': search_id})


@app.route('/get_results/<search_id>', methods=['GET'])
def get_results(search_id):
    global search_completed  # Reference the global dictionary
    print(f"Getting results for search ID: {search_id}")  # Debugging line
    
    # Check if the search has completed
    if search_id in search_completed:
        if search_completed[search_id]:
            with search_results_lock:
                print(f"Available search results: {list(search_results.keys())}")  # Debugging
                results = search_results.get(search_id)
                if results is not None:
                    return jsonify({
                        'path': results['path'],
                        'time': results['time'],
                        'discovered': results['discovered'],
                        'completed': results['completed'],
                        'error': results['error'],
                        'search_method': results['search_method'],
                        'path_length': results['path_length'],
                    }), 200
                else:
                    return jsonify({'message': 'Search completed but no results found'}), 404
        else:
            return jsonify({'message': 'Search is still in progress'}), 200
    else:
        return jsonify({'message': 'Search ID not found'}), 404


@app.route('/logs', methods=['GET'])
def stream_logs():
    def generate():
        while True:
            if not logs_queue.empty():
                log = logs_queue.get()
                yield f"data: {log}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/abort_search', methods=['POST'])
def abort_search():
    abort_search_event.set()
    with logs_queue.mutex:
        logs_queue.queue.clear()
    abort_search_event.clear()
    return jsonify({'message': 'Search abort initiated'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
