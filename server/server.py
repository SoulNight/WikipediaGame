from flask import Flask, request, jsonify, send_from_directory, Response # type: ignore
from flask_limiter import Limiter # type: ignore
from flask_limiter.util import get_remote_address # type: ignore
from crawler import abort_search_event, breadth_first_search, bidirectional_search, depth_first_search
from queue import Queue
from threading import Thread, Lock
import time
import uuid

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
    # Initialize default values
    path = None
    discovered = 0
    error_message = None  # Add an error message variable to capture exception details
    start_time = time.time()  # Start time should be defined outside of the try-except block

    try:
        # Reset the abort_search_event at the start of each new search
        abort_search_event.clear()

        # Implement the search logic here
        if search_method == 'bidirectional':
            path, time_elapsed, discovered, search_method = bidirectional_search(start_page, finish_page, logs_queue)
        elif search_method == 'breadth-first':
            path, time_elapsed, discovered, search_method = breadth_first_search(start_page, finish_page, logs_queue)
        elif search_method == 'depth-first':
            path, time_elapsed, discovered, search_method = depth_first_search(start_page, finish_page, logs_queue)

    except Exception as e:
        error_message = str(e)  # Store the exception message in error_message
        logs_queue.put(f"Search {search_id} error: {error_message}")
        print(f"Search {search_id} failed with error: {error_message}")
        time_elapsed = time.time() - start_time  # Ensure time_elapsed is defined in case of an exception

    # Calculate the time after search has completed or failed
    search_time = time.time() - start_time
    path_length = len(path) if path else 0  # Set path_length here

    # No matter what happens, store the results (even if they are None or defaults)
    with search_results_lock:
        search_results[search_id] = {
            'path': path,
            'time': search_time,
            'discovered': discovered,
            'completed': path is not None,
            'error': error_message,
            'search_method': search_method,
            'path_length': path_length,  # Now it's guaranteed to be set
        }

        # Prepare the completion message only if there's an error
        if error_message:
            error_completion_message = f"Search {search_id} error: {error_message}"
            print(error_completion_message)
            logs_queue.put(error_completion_message)
        else:
            # You can still print the completion message in the server console if needed
            print(f"Search {search_id} completed successfully.")
            # Do not add the success message to logs_queue here


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
    with search_results_lock:
        results = search_results.get(search_id)
        if results is not None:
            if results.get('completed', False):
                # Search has completed
                response = jsonify({
                    'path': results['path'],
                    'time': results['time'],
                    'discovered': results['discovered'],
                    'completed': results['completed'],
                    'error': results['error'],
                    'search_method': results['search_method'],
                    'path_length': results['path_length'],
                })
                return response, 200
            else:
                # Search is still in progress
                return jsonify({'message': 'Search is in progress'}), 202
        else:
            # No search with the given ID was found
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
    abort_search_event.set()  # Signal that an abort has been requested

    # Clear the logs queue
    with logs_queue.mutex:
        logs_queue.queue.clear()

    # Clear the abort_search_event after aborting to reset for the next search
    abort_search_event.clear()

    return jsonify({'message': 'Search abort initiated'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
