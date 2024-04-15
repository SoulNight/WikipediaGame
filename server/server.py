from flask import Flask, request, jsonify, send_from_directory, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from crawler import abort_search_event, breadth_first_search, bidirectional_search
from queue import Queue
from threading import Thread, Lock
import time
import uuid

# Set the rate limit for requests
RATE_LIMIT = "5/minute"

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
    # Initialize default values
    path = None
    time_elapsed = 0
    discovered = 0

    try:
        # Reset the abort_search_event at the start of each new search
        abort_search_event.clear()
        
        # Implement the search logic here
        if search_method == 'bidirectional':
            path, time_elapsed, discovered = bidirectional_search(start_page, finish_page, logs_queue)
        elif search_method == 'breadth-first':
            path, time_elapsed, discovered = breadth_first_search(start_page, finish_page, logs_queue)
        
    except Exception as e:
        # If there is an exception, log it and store it with the results
        print(f"Search {search_id} failed: {e}")
 
    # No matter what happens, store the results (even if they are None or defaults)
    with search_results_lock:
        search_results[search_id] = {
            'path': path,
            'time': time_elapsed,
            'discovered': discovered,
            'completed': path is not None  # This line sets the completed flag
        }
        print(f"Search {search_id} completed. Path: {path}, Time: {time_elapsed}, Discovered: {discovered}")


@app.route('/find_path', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def find_path():
    # Safely attempt to get JSON data from the request
    data = request.get_json()
    
    # Reset the abort_search_event before starting a new search
    abort_search_event.clear()
    
    # Use .get to avoid KeyError and provide default values as None
    start_page = data.get('start')
    finish_page = data.get('finish')
    search_method = data.get('method', 'breadth-first')
    
    # Validate that required information was provided
    if not start_page or not finish_page:
        # Return a meaningful error response
        return jsonify({'message': 'Missing "start" or "finish" parameters'}), 400
    
    # Continue with search ID and thread starting logic
    search_id = str(uuid.uuid4())
    search_thread = Thread(target=search_and_log, args=(start_page, finish_page, search_method, search_id))
    search_thread.start()
    return jsonify({'message': 'Search started', 'search_id': search_id}), 202

@app.route('/get_results/<search_id>', methods=['GET'])
def get_results(search_id):
    # Wait for up to 10 seconds for the search to complete
    for _ in range(10):
        with search_results_lock:
            results = search_results.get(search_id)
            if results is not None and results.get('completed', False):
                # Remove the results after fetching to clean up memory
                del search_results[search_id]
                return jsonify(results), 200
        time.sleep(1)
    # If the results are not ready after 10 seconds, return a 404
    return jsonify({'message': 'Search results not ready or not found.'}), 404

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
    abort_search_event.set()  # Signal that an abort has been requested
    
    # Clear the logs queue
    with logs_queue.mutex:
        logs_queue.queue.clear()

    # Clear the abort_search_event after aborting to reset for the next search
    abort_search_event.clear()
    
    return jsonify({'message': 'Search abort initiated'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
