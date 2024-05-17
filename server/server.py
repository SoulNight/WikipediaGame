import os  # Importing os for operating system related functionality
import ssl  # Importing ssl for SSL support
import nltk  # Importing nltk for natural language processing tasks
import time  # Importing time for time-related functions
import uuid  # Importing uuid for generating unique identifiers
from flask import Flask, request, jsonify, send_from_directory, Response  # Importing Flask modules for web server functionality
from flask_limiter import Limiter  # Importing Limiter for rate limiting in Flask
from flask_limiter.util import get_remote_address  # Importing get_remote_address for IP address handling in Flask
from threading import Thread, Lock  # Importing Thread and Lock for thread-related operations
from queue import Queue  # Importing Queue for implementing a FIFO queue
from crawler import abort_search_event, breadth_first_search, bidirectional_search, a_star  # Importing search algorithms from crawler module
import logging  # Importing logging for logging functionality
from threading import Thread, Event, Timer  # Importing Thread, Event, and Timer for thread-related operations
from crawler import precompute_finish_page_keywords  # Importing function for precomputing finish page keywords from crawler module


# Define a class named StoppableThread, inheriting from Thread
class StoppableThread(Thread):
    # Constructor method to initialize the thread
    def __init__(self, timeout=None, *args, **kwargs):
        # Remove the custom 'timeout' argument before calling the superclass constructor
        self._timeout = timeout
        kwargs.pop('timeout', None)  # Remove timeout from kwargs if it exists to prevent TypeError
        super().__init__(*args, **kwargs)  # Call superclass constructor with remaining args and kwargs
        self._stop_event = Event()  # Initialize stop event to synchronize thread termination
        self._start_time = None  # Initialize start time of the thread

    # Method representing the thread's execution
    def run(self):
        # If timeout is specified, set up a timer to stop the thread after the timeout period
        if self._timeout:
            timer = Timer(self._timeout, self.stop)  # Setup a timer that will stop the thread after the timeout period
            timer.start()  # Start the timer
        try:
            super().run()  # Call superclass run method to execute the thread's work
        finally:
            # If timeout is specified and the work completes before the timeout, cancel the timer
            if self._timeout:
                timer.cancel()  # Cancel the timer if the work completes before the timeout

    # Method to stop the thread's execution
    def stop(self):
        self._stop_event.set()  # Set the stop event to signal the thread to stop execution

    # Method to check if the thread has stopped
    def stopped(self):
        return self._stop_event.is_set()  # Check if the stop event is set, indicating thread termination

# Configure the logging level for the application to INFO
logging.basicConfig(level=logging.INFO)


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

# Decorator specifying that this function handles GET requests to the root URL ('/')
@app.route('/', methods=['GET'])
def home():
    # Serve 'index.html' from the static_folder
    return send_from_directory(app.static_folder, 'index.html')



# Define a function named search_and_log that takes start and finish page URLs, search method, and search ID as input
def search_and_log(start_page, finish_page, search_method, search_id):
    # Access global variables
    global search_completed, search_states

    # Set initial search state to incomplete
    search_states[search_id] = {'completed': False}
    
    # Precompute and cache the finish page keywords if A* search is selected
    if search_method == 'a_star':
        precompute_finish_page_keywords(finish_page)

    # Print a confirmation message with search ID
    print(f"Search and log called with search_id: {search_id}")

    # Initialize variables
    path = None
    discovered = 0
    total_links = 0  # To keep the total number of links found
    error_message = None
    start_time = time.time()

    # Initialize the search as incomplete
    search_completed[search_id] = False
    try:
        abort_search_event.clear()
        # Execute the search based on the selected search method
        print(search_method)
        if search_method == 'bidirectional':
            path, time_elapsed, discovered, search_method, total_links = bidirectional_search(start_page, finish_page, logs_queue, search_id)
        if search_method == 'breadth-first':
            path, time_elapsed, discovered, search_method, total_links = breadth_first_search(start_page, finish_page, logs_queue, search_id)
        elif search_method == 'a_star':
            path, time_elapsed, discovered, search_method, total_links = a_star(start_page, finish_page, logs_queue, search_id)
            
        print(f"Search {search_id} completed. Path found: {path}")
        

        # If a path is found, set the search state to completed
        if path:
            search_states[search_id]['completed'] = True
            logs_queue.put(f"Search {search_id} completed. Path found: {path}")
        else:
            logs_queue.put(f"Search {search_id} concluded without finding a path.")

    except Exception as e:
        # Handle any exceptions and log the error message
        error_message = f"{type(e).__name__}: {str(e)}"
        logs_queue.put(f"Search {search_id} error: {error_message}")
        print(f"Search {search_id} failed with error: {error_message}")
        time_elapsed = time.time() - start_time

    finally:
        # Ensure the following code runs regardless of exceptions

        # Calculate search time and path length
        search_time = time.time() - start_time
        path_length = len(path) if path else 0

        # Update search_results dictionary with search information
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
        print("abc")
        # Mark the search as completed
        search_completed[search_id] = True

        # Log completion or error message
        if error_message:
            error_completion_message = f"Search {search_id} error: {error_message}"
            print(error_completion_message)
            logs_queue.put(error_completion_message)
        else:
            print(f"Search {search_id} completed successfully.")

        # Sleep to ensure clean thread shutdown
        time.sleep(1)


# Decorator specifying that this function handles POST requests to the '/find_path' endpoint
@app.route('/find_path', methods=['POST'])
def find_path():
    # Retrieve JSON data from the request
    data = request.get_json()
    
    # Extract start page, finish page, and search method from the JSON data
    start_page = data.get('start')
    finish_page = data.get('finish')
    search_method = data.get('method', 'breadth-first')  # Default to 'breadth-first' if method is not provided
    timeout = 300  # Example: 300 seconds timeout

    # Check if start and finish pages are provided
    if not start_page or not finish_page:
        return jsonify({'message': 'Missing parameters'}), 400  # Return error message and status code 400 for missing parameters

    # Generate a unique search ID using UUID
    search_id = str(uuid.uuid4())

    # Create a StoppableThread for executing the search_and_log function with the provided parameters
    search_thread = StoppableThread(target=search_and_log, args=(start_page, finish_page, search_method, search_id), timeout=300)

    # Start the search thread
    search_thread.start()

    # Return a JSON response indicating that the search has started along with the search ID
    return jsonify({'message': 'Search started', 'search_id': search_id})



# Decorator specifying that this function handles GET requests to the '/get_results/<search_id>' endpoint
@app.route('/get_results/<search_id>', methods=['GET'])
def get_results(search_id):
    global search_completed  # Reference the global dictionary

    # Debugging line to print search ID
    print(f"Getting results for search ID: {search_id}")
    # Check if the search has completed
    if search_id in search_completed:
        if search_completed[search_id]:
            # If search is completed, retrieve and return the results
            with search_results_lock:
                # Debugging line to print available search results
                print(f"Available search results: {list(search_results.keys())}")

                # Get the results for the provided search ID
                results = search_results.get(search_id)

                # Check if results are available for the search ID
                if results is not None:
                    # Return the results as a JSON response with status code 200 (OK)
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
                    # Return a message indicating that the search completed but no results were found with status code 404 (Not Found)
                    return jsonify({'message': 'Search completed but no results found'}), 404
        else:
            # Return a message indicating that the search is still in progress with status code 200 (OK)
            return jsonify({'message': 'Search is still in progress'}), 200
    else:
        # Return a message indicating that the provided search ID was not found with status code 404 (Not Found)
        return jsonify({'message': 'Search ID not found'}), 404


# Route to stream logs via Server-Sent Events
@app.route('/logs', methods=['GET'])
def stream_logs():
    def generate():
        while True:
            # Check if the logs queue is not empty
            if not logs_queue.empty():
                # Get the next log from the queue and yield it as a Server-Sent Event
                log = logs_queue.get()
                yield f"data: {log}\n\n"  # Yield the log in the required format for Server-Sent Events
            time.sleep(1)  # Sleep for 1 second before checking the logs queue again

    # Return a Response object with the generator function and set the MIME type to text/event-stream
    return Response(generate(), mimetype='text/event-stream')


# Route to abort an ongoing search
@app.route('/abort_search', methods=['POST'])
def abort_search():
    # Set the abort search event to signal the threads to stop searching
    abort_search_event.set()
    
    # Clear the logs queue to remove any pending logs related to the aborted search
    with logs_queue.mutex:
        logs_queue.queue.clear()
    
    # Clear the abort search event flag
    abort_search_event.clear()
    
    # Return a JSON response indicating that the search abort has been initiated
    return jsonify({'message': 'Search abort initiated'}), 200

# Entry point of the application
if __name__ == '__main__':
    # Run the Flask application with the specified host, port, debug mode, and threaded mode
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)

