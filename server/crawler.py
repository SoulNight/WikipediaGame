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
from collections import deque
import heapq
from functools import lru_cache
from nltk.corpus import wordnet
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from requests import Session
from collections import namedtuple

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

# Function to extract keywords from text
def extract_keywords(text):
    words = word_tokenize(text)
    stopwords_set = set(stopwords.words('english')).union(additional_stopwords)
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stopwords_set]
    tagged_words = pos_tag(filtered_words)
    keywords = [word for word, tag in tagged_words if tag in {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}]
    freq_dist = FreqDist(keywords)
    significant_keywords = {word: freq for word, freq in freq_dist.items() if freq > 1 and len(word) > 1}
    return significant_keywords

@lru_cache(maxsize=100)
def get_page_text(url):
    try:
        response = session.get(url)  # Use the session object here
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(p.text for p in soup.find_all('p'))
        return text
    except requests.exceptions.RequestException as e:
        logs_queue.put(f"Failed to retrieve page: {url} with error: {e}")
        return ''

@lru_cache(maxsize=100)
def get_page_keywords(url):
    text = get_page_text(url)
    return extract_keywords(text)


def get_links(page_url, logs_queue, search_id):
    global search_states
    if search_states.get(search_id, {}).get('completed', False) or abort_search_event.is_set():
        return [], 0
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True)]
        total_links_count = len(all_links)
        valid_links = [link for link in all_links if '#' not in link and re.match(r'^https://en\.wikipedia\.org/wiki/[^:]*$', link)]
        logs_queue.put(f"Found {len(valid_links)} valid links on page: {page_url}")
        logs_queue.put(f"Found {total_links_count} total links on page: {page_url}")
        return valid_links, total_links_count
    except requests.exceptions.RequestException as e:
        error_type = type(e).__name__
        logs_queue.put(f"Failed to retrieve page: {page_url} with error [{error_type}]: {e}")
        return [], 0

def heuristic_by_content(current_page):
    global finish_page_keywords_cache
    current_keywords = get_page_keywords(current_page)
    score = sum(current_keywords[word] * count for word, count in finish_page_keywords_cache.items() if word in current_keywords)
    max_possible_score = sum(finish_page_keywords_cache.values())
    normalized_score = score / max_possible_score if max_possible_score else 0
    distance = 1 - normalized_score
    return distance

def precompute_finish_page_keywords(finish_page):
    global finish_page_keywords_cache
    finish_text = get_page_text(finish_page)
    finish_page_keywords_cache = extract_keywords(finish_text)


def a_star(start_page, finish_page, logs_queue, search_id):
    global search_states, finish_page_keywords_cache

    # Ensure the finish page keywords are precomputed
    assert finish_page_keywords_cache is not None, "Finish page keywords are not precomputed"

    open_set = []
    heapq.heappush(open_set, (0, start_page, [start_page]))  # Cost from start, page URL, path list
    g_costs = {start_page: 0}
    closed_set = set()
    total_links_count = 0
    start_time = time.time()

    while open_set and not search_states.get(search_id, {}).get('completed', False):
        if abort_search_event.is_set():
            logs_queue.put(f"Search {search_id} aborted by user request.")
            return None, time.time() - start_time, len(g_costs), 'a_star', total_links_count

        _, current_page, path = heapq.heappop(open_set)

        if current_page == finish_page:
            logs_queue.put(f"Search {search_id} completed. Path found: {path}")
            return path, time.time() - start_time, len(g_costs), 'a_star', total_links_count

        closed_set.add(current_page)
        valid_links, page_links_count = get_links(current_page, logs_queue, search_id)
        total_links_count += page_links_count

        for neighbor in valid_links:
            if neighbor in closed_set:
                continue

            tentative_g_cost = g_costs[current_page] + 1

            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g_cost
                heuristic_cost = heuristic_by_content(neighbor)  # Use content-based heuristic directly
                estimated_total_cost = tentative_g_cost + heuristic_cost
                heapq.heappush(open_set, (estimated_total_cost, neighbor, path + [neighbor]))

    logs_queue.put(f"Search {search_id} concluded without finding a path.")
    return None, time.time() - start_time, len(g_costs), 'a_star', total_links_count


# BFS - this function includes the MAIN PAGE from the search
def breadth_first_search(start_page, finish_page, logs_queue, search_id):
    queue = deque([(start_page, [start_page])])
    discovered = set([start_page])
    start_time = time.time()
    total_links_count = 0

    while queue:
        if abort_search_event.is_set():
            logs_queue.put(f"Search {search_id} aborted by user request.")
            return None, time.time() - start_time, len(discovered), 'breadth-first', total_links_count

        current_vertex, path = queue.popleft()
        logs_queue.put(f"Dequeued: {current_vertex}, Path: {path}")
        
        valid_links, page_links_count = get_links(current_vertex, logs_queue, search_id)
        total_links_count += page_links_count

        for next_page in set(valid_links) - discovered:
            discovered.add(next_page)
            new_path = path + [next_page]
            logs_queue.put(f"Enqueueing: {next_page}, New path: {new_path}")

            if next_page == finish_page:
                logs_queue.put(f"Finish page found: {next_page}, Final path: {new_path}")
                return new_path, time.time() - start_time, len(discovered), 'breadth-first', total_links_count

            queue.append((next_page, new_path))

    logs_queue.put(f"Search {search_id} concluded without finding the finish page.")
    return None, time.time() - start_time, len(discovered), 'breadth-first', total_links_count


# Bidirectional search - this function includes the MAIN PAGE in the search - 
def bidirectional_search(start_page, finish_page, logs_queue, search_id):
    global search_states

    if start_page == finish_page:
        logs_queue.put("Start and finish pages are the same for search_id: {}".format(search_id))
        return [start_page], 0, 1, 'bidirectional', 1

    start_queue = deque([(start_page, [start_page])])
    finish_queue = deque([(finish_page, [finish_page])])
    start_visited = {start_page: [start_page]}
    finish_visited = {finish_page: [finish_page]}
    total_links_count = 0

    start_time = time.time()

    while start_queue and finish_queue:
        if search_states.get(search_id, {}).get('completed', False) or abort_search_event.is_set():
            logs_queue.put("Search {} aborted or already completed.".format(search_id))
            return None, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count

        current_start, path_start = start_queue.popleft()
        start_valid_links, start_page_links_count = get_links(current_start, logs_queue, search_id)
        total_links_count += start_page_links_count

        for link in start_valid_links:
            if link not in start_visited:
                start_visited[link] = path_start + [link]
                start_queue.append((link, start_visited[link]))
                if link in finish_visited:
                    combined_path = start_visited[link] + finish_visited[link][::-1][1:]
                    return combined_path, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count

        current_finish, path_finish = finish_queue.popleft()
        finish_valid_links, finish_page_links_count = get_links(current_finish, logs_queue, search_id)
        total_links_count += finish_page_links_count

        for link in finish_valid_links:
            if link not in finish_visited:
                finish_visited[link] = path_finish + [link]
                finish_queue.append((link, finish_visited[link]))
                if link in start_visited:
                    combined_path = finish_visited[link][:-1] + start_visited[link][::-1]
                    return combined_path[::-1], time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count

    logs_queue.put("Search {} concluded without finding a path.".format(search_id))
    return None, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional', total_links_count
