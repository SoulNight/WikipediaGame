import requests  # Importing the requests library for making HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for web scraping
from urllib.parse import urljoin  # Importing urljoin for URL manipulation
import nltk  # Importing the Natural Language Toolkit library
from nltk.corpus import stopwords  # Importing NLTK's stopwords corpus
from collections import Counter  # Importing Counter for counting occurrences
import time  # Importing the time module for time-related functions
from queue import PriorityQueue, Queue  # Importing Queue and PriorityQueue for implementing data structures
import re  # Importing re for regular expressions
import requests_cache  # Importing requests_cache for caching HTTP responses
from flask import Flask, request, jsonify, send_from_directory, Response  # Importing Flask modules for web server functionality
from flask_limiter import Limiter  # Importing Limiter for rate limiting in Flask
from flask_limiter.util import get_remote_address  # Importing get_remote_address for IP address handling in Flask
from threading import Event  # Importing Event for synchronization between threads
from collections import deque  # Importing deque for implementing a double-ended queue
import heapq  # Importing heapq for heap queue algorithm
from functools import lru_cache  # Importing lru_cache for memoization
from nltk.corpus import wordnet  # Importing NLTK's WordNet corpus for lexical database
from nltk.probability import FreqDist  # Importing FreqDist for frequency distribution
from nltk.tokenize import word_tokenize  # Importing word_tokenize for tokenization
from nltk import pos_tag  # Importing pos_tag for part-of-speech tagging
from requests import Session  # Importing Session for HTTP session management
from collections import namedtuple  # Importing namedtuple for creating named tuples

# Add any domain-specific stopwords
additional_stopwords = {'example', 'another_word', 'more_noise'}

# Global cache for finish page keywords
finish_page_keywords_cache = None
search_states = {}

# Download necessary NLTK packages
nltk.download('punkt')  # Downloading the 'punkt' tokenizer model
nltk.download('stopwords')  # Downloading the stopwords corpus
nltk.download('averaged_perceptron_tagger')  # POS tagger

# Initialize caching for requests
session = Session()  # Creating a session object for making HTTP requests
requests_cache.install_cache('my_cache')  # Setting up a cache for HTTP responses

# Event for aborting the search
abort_search_event = Event()  # Creating an event object for aborting the search

# Queue for logging messages
logs_queue = Queue()  # Creating a queue for logging messages

# Define a function named extract_keywords that takes a text as input
def extract_keywords(text):
    # Tokenize the input text into words
    words = word_tokenize(text)
    
    # Create a set of English stopwords and union it with additional stopwords
    stopwords_set = set(stopwords.words('english')).union(additional_stopwords)
    
    # Filter out non-alphanumeric words and stopwords, converting them to lowercase
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stopwords_set]
    
    # Tag the filtered words with their parts of speech
    tagged_words = pos_tag(filtered_words)
    
    # Extract words that are nouns (singular and plural) or verbs (various forms)
    keywords = [word for word, tag in tagged_words if tag in {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}]
    
    # Create a frequency distribution of the extracted keywords
    freq_dist = FreqDist(keywords)
    
    # Filter out keywords that occur less than twice and have a length greater than one character
    significant_keywords = {word: freq for word, freq in freq_dist.items() if freq > 1 and len(word) > 1}
    
    # Return the dictionary of significant keywords
    return significant_keywords


# Decorator to cache results of the function with a maximum size of 100
@lru_cache(maxsize=100)
# Define a function named get_page_text that takes a URL as input
def get_page_text(url):
    try:
        # Make a GET request to the URL using the session object
        response = session.get(url)
        # Raise an exception if the response status code is not OK
        response.raise_for_status()
        # Parse the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from all <p> tags and join them into a single string
        text = ' '.join(p.text for p in soup.find_all('p'))
        # Return the extracted text
        return text
    except requests.exceptions.RequestException as e:
        # Log the failure to retrieve the page along with the error message
        logs_queue.put(f"Failed to retrieve page: {url} with error: {e}")
        # Return an empty string in case of failure
        return ''


# Decorator to cache results of the function with a maximum size of 100
@lru_cache(maxsize=100)
# Define a function named get_page_keywords that takes a URL as input
def get_page_keywords(url):
    # Get the text content of the page from the provided URL
    text = get_page_text(url)
    
    # Extract significant keywords from the page text using the extract_keywords function
    keywords = extract_keywords(text)
    
    # Return the extracted keywords
    return keywords


# Define a function named get_links that takes a page URL, logs queue, and search ID as input
def get_links(page_url, logs_queue, search_id):
    # Access the global variable search_states
    global search_states
    
    # Check if the search is completed or if the search has been aborted
    if search_states.get(search_id, {}).get('completed', False) or abort_search_event.is_set():
        # If either condition is met, return an empty list of links and a link count of 0
        return [], 0
    
    try:
        # Make a GET request to the page URL
        response = requests.get(page_url)
        response.raise_for_status()  # Raise an exception if the response status code is not OK
        
        # Parse the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all links from the page and join them with the base URL
        all_links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True)]
        
        # Count the total number of links found on the page
        total_links_count = len(all_links)
        
        # Filter out invalid links (links with '#' and links not pointing to Wikipedia articles)
        valid_links = [link for link in all_links if '#' not in link and re.match(r'^https://en\.wikipedia\.org/wiki/[^:]*$', link)]
        
        # Log the number of valid links found on the page
        logs_queue.put(f"Found {len(valid_links)} valid links on page: {page_url}")
        
        # Log the total number of links found on the page
        logs_queue.put(f"Found {total_links_count} total links on page: {page_url}")
        
        # Return the list of valid links and the total number of links
        return valid_links, total_links_count
    
    except requests.exceptions.RequestException as e:
        # Log the failure to retrieve the page along with the error message
        error_type = type(e).__name__
        logs_queue.put(f"Failed to retrieve page: {page_url} with error [{error_type}]: {e}")
        
        # Return an empty list of links and a link count of 0
        return [], 0



# Define a function named precompute_finish_page_keywords that takes a finish page URL as input
def precompute_finish_page_keywords(finish_page):
    # Access the global variable finish_page_keywords_cache
    global finish_page_keywords_cache
    
    # Get the text content of the finish page
    finish_text = get_page_text(finish_page)
    
    # Extract keywords from the finish page text and store them in the finish_page_keywords_cache
    finish_page_keywords_cache = extract_keywords(finish_text)

def heuristic_by_content(current_page, finish_page_keywords_cache):
    # Get the keywords from the current page using the get_page_keywords function
    current_keywords = get_page_keywords(current_page)
    
    # Calculate the Jaccard similarity coefficient between the current page keywords and finish page keywords
    intersection = set(current_keywords.keys()) & set(finish_page_keywords_cache.keys())
    union = set(current_keywords.keys()) | set(finish_page_keywords_cache.keys())
    similarity = len(intersection) / len(union) if union else 0
    
    # Calculate the distance as 1 minus the similarity
    distance = 1 - similarity
    
    # Return the calculated distance
    return distance

# Define a function named a_star that takes start and finish page URLs, logs queue, and search ID as input
def a_star(start_page, finish_page, logs_queue, search_id):
    # Use global variables for search states and finish page keywords cache
    global search_states, finish_page_keywords_cache

    # Ensure the finish page keywords are precomputed
    assert finish_page_keywords_cache is not None, "Finish page keywords are not precomputed"

    # Initialize the open set with the start page and its path
    open_set = []
    heapq.heappush(open_set, (0, start_page, [start_page]))
    
    # Dictionary to store the cost of the path from the start page to the current page
    g_costs = {start_page: 0}
    
    # Set to keep track of the pages that have already been evaluated
    closed_set = set()
    
    # Initialize the total count of links processed
    total_links_count = 0
    
    # Record the start time of the search
    start_time = time.time()

    # Continue the search while there are pages to evaluate and the search is not completed
    while open_set and not search_states.get(search_id, {}).get('completed', False):
        # Check if the search has been aborted
        if abort_search_event.is_set():
            logs_queue.put(f"Search {search_id} aborted by user request.")
            return None, time.time() - start_time, len(g_costs), 'a_star', total_links_count

        # Get the page with the lowest estimated cost from the open set
        _, current_page, path = heapq.heappop(open_set)

        # If the current page is the finish page, return the successful path
        if current_page == finish_page:
            logs_queue.put(f"Search {search_id} completed. Path found: {path}")
            return path, time.time() - start_time, len(g_costs), 'a_star', total_links_count

        # Add the current page to the closed set
        closed_set.add(current_page)

        # Retrieve valid links from the current page and update the total link count
        valid_links, page_links_count = get_links(current_page, logs_queue, search_id)
        total_links_count += page_links_count

        # Evaluate each neighbor linked from the current page
        for neighbor in valid_links:
            # Skip the neighbor if it has already been evaluated
            if neighbor in closed_set:
                continue

            # Calculate the tentative cost to reach the neighbor
            tentative_g_cost = g_costs[current_page] + 1

            # If the neighbor has not been evaluated or a shorter path to it is found
            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                # Update the cost to reach the neighbor
                g_costs[neighbor] = tentative_g_cost
                # Estimate the total cost using the heuristic
                heuristic_cost = heuristic_by_content(neighbor, finish_page_keywords_cache)
                estimated_total_cost = tentative_g_cost + heuristic_cost
                # Add the neighbor to the open set with the updated path
                heapq.heappush(open_set, (estimated_total_cost, neighbor, path + [neighbor]))

                # If the neighbor is the finish page, return the successful path
                if neighbor == finish_page:
                    logs_queue.put(f"Search {search_id} completed. Path found: {path + [neighbor]}")
                    return path + [neighbor], time.time() - start_time, len(g_costs), 'a_star', total_links_count

    # If no path is found, log the conclusion and return the search details
    logs_queue.put(f"Search {search_id} concluded without finding a path.")
    return None, time.time() - start_time, len(g_costs), 'a_star', total_links_count



# Define a function named breadth_first_search that takes start and finish page URLs, logs queue, and search ID as input
def breadth_first_search(start_page, finish_page, logs_queue, search_id):
    # Initialize queue with start page and discovered set with start page
    queue = deque([(start_page, [start_page])])
    discovered = set([start_page])
    
    # Record start time and initialize total links count
    start_time = time.time()
    total_links_count = 0

    # Main loop: continue until queue is empty
    while queue:
        # Check if search has been aborted
        if abort_search_event.is_set():
            logs_queue.put(f"Search {search_id} aborted by user request.")
            return None, time.time() - start_time, len(discovered), 'breadth-first', total_links_count

        # Dequeue a vertex and its path
        current_vertex, path = queue.popleft()
        logs_queue.put(f"Dequeued: {current_vertex}, Path: {path}")
        
        # Get valid links from the current vertex and count page links
        valid_links, page_links_count = get_links(current_vertex, logs_queue, search_id)
        total_links_count += page_links_count

        # Explore neighbors of the current vertex
        for next_page in set(valid_links) - discovered:
            discovered.add(next_page)
            new_path = path + [next_page]
            logs_queue.put(f"Enqueueing: {next_page}, New path: {new_path}")

            # Check if finish page is reached
            if next_page == finish_page:
                logs_queue.put(f"Finish page found: {next_page}, Final path: {new_path}")
                return new_path, time.time() - start_time, len(discovered), 'breadth-first', total_links_count

            # Enqueue the neighbor and its new path
            queue.append((next_page, new_path))

    # If the loop completes without finding the finish page, log and return
    logs_queue.put(f"Search {search_id} concluded without finding the finish page.")
    return None, time.time() - start_time, len(discovered), 'breadth-first', total_links_count


# Define a function named bidirectional_search that takes start and finish page URLs, logs queue, and search ID as input
def bidirectional_search(start_page, finish_page, logs_queue, search_id):
    # Access global variable
    global search_states

    # If start and finish pages are the same, return immediately
    if start_page == finish_page:
        logs_queue.put("Start and finish pages are the same for search_id: {}".format(search_id))
        return [start_page], 0, 1, 'bidirectional', 1

    # Initialize queues, visited sets, total links count, and start time
    start_queue = deque([(start_page, [start_page])])
    finish_queue = deque([(finish_page, [finish_page])])
    start_visited = {start_page: [start_page]}
    finish_visited = {finish_page: [finish_page]}
    total_links_count = 0
    start_time = time.time()

    # Main loop: continue until either queue becomes empty
    while start_queue and finish_queue:
        # Check if search has been completed or aborted
        if search_states.get(search_id, {}).get('completed', False) or abort_search_event.is_set():
            logs_queue.put("Search {} aborted or already completed.".format(search_id))
            return None, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count

        # Process nodes from the start queue
        current_start, path_start = start_queue.popleft()
        start_valid_links, start_page_links_count = get_links(current_start, logs_queue, search_id)
        total_links_count += start_page_links_count

        # Explore neighbors of the current start node
        for link in start_valid_links:
            if link not in start_visited:
                start_visited[link] = path_start + [link]
                start_queue.append((link, start_visited[link]))
                # Check if a meeting point is found
                if link in finish_visited:
                    combined_path = start_visited[link] + finish_visited[link][::-1][1:]
                    return combined_path, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count

        # Process nodes from the finish queue
        current_finish, path_finish = finish_queue.popleft()
        finish_valid_links, finish_page_links_count = get_links(current_finish, logs_queue, search_id)
        total_links_count += finish_page_links_count

        # Explore neighbors of the current finish node
        for link in finish_valid_links:
            if link not in finish_visited:
                finish_visited[link] = path_finish + [link]
                finish_queue.append((link, finish_visited[link]))
                # Check if a meeting point is found
                if link in start_visited:
                    combined_path = finish_visited[link][:-1] + start_visited[link][::-1]
                    return combined_path[::-1], time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count

    # If the loop completes without finding a path, log and return
    logs_queue.put("Search {} concluded without finding a path.".format(search_id))
    return None, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count
