import time
import requests
from bs4 import BeautifulSoup
import re
import requests_cache
from threading import Event
from urllib.parse import urljoin
from queue import Queue  # Import Queue for thread-safe logging

# This event will be set when the search should be aborted.
abort_search_event = Event()

# TIMEOUT = 20  # time limit in seconds for the search
TIMEOUT = 1000  # time limit in seconds for the search

# Initialize caching
requests_cache.install_cache('my_cache')

def get_links(page_url, logs_queue):
    try:
        response = requests.get(page_url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True) if '#' not in a['href']]
        links = [link for link in all_links if re.match(r'^https://en\.wikipedia\.org/wiki/[^:]*$', link)]
        logs_queue.put(f"Found {len(links)} links on page: {page_url}")
        return links
    except requests.exceptions.RequestException as e:
        logs_queue.put(f"Failed to retrieve page: {page_url} with error: {e}")
        return []  # Return an empty list if the request failed


def breadth_first_search(start_page, finish_page, logs_queue):
    queue = [(start_page, [start_page])]
    discovered = set([start_page])
    start_time = time.time()

    while queue:
        if abort_search_event.is_set():
            logs_queue.put("Search aborted by user request.")
            return None, time.time() - start_time, len(discovered)

        (vertex, path) = queue.pop(0)
        for next in set(get_links(vertex, logs_queue)) - discovered:
            if next == finish_page:
                logs_queue.put(f"Found finish page: {next}")
                return path + [next], time.time() - start_time, len(discovered)
            discovered.add(next)
            queue.append((next, path + [next]))

    logs_queue.put("Search concluded without finding the finish page.")
    return None, time.time() - start_time, len(discovered)

def bidirectional_search(start_page, finish_page, logs_queue):
    if start_page == finish_page:
        logs_queue.put("Start and finish pages are the same.")
        return [start_page], 0, 1

    start_queue = [(start_page, [start_page])]
    finish_queue = [(finish_page, [finish_page])]
    start_visited = {start_page: [start_page]}
    finish_visited = {finish_page: [finish_page]}
    start_time = time.time()

    while start_queue and finish_queue:
        if abort_search_event.is_set():
            logs_queue.put("Search aborted by user request.")
            return None, time.time() - start_time, len(start_visited) + len(finish_visited)
        
        # Expand the front from the start
        current_start, path_start = start_queue.pop(0)
        start_links = get_links(current_start, logs_queue)
        for link in start_links:
            if link not in start_visited:
                start_visited[link] = path_start + [link]
                start_queue.append((link, start_visited[link]))
                if link in finish_visited:
                    logs_queue.put(f"Path found connecting through: {link}")
                    combined_path = start_visited[link]
                    if link not in (start_page, finish_page):
                        combined_path += finish_visited[link][-2::-1]
                    else:
                        combined_path += finish_visited[link][::-1]
                    logs_queue.put(f"Combined path: {combined_path}")
                    return combined_path, time.time() - start_time, len(start_visited) + len(finish_visited)

        # Expand the front from the finish
        current_finish, path_finish = finish_queue.pop(0)
        finish_links = get_links(current_finish, logs_queue)
        for link in finish_links:
            if link not in finish_visited:
                finish_visited[link] = path_finish + [link]
                finish_queue.append((link, finish_visited[link]))
                if link in start_visited:
                    logs_queue.put(f"Path found connecting through: {link}")
                    combined_path = start_visited[link]
                    if link not in (start_page, finish_page):
                        combined_path += finish_visited[link][-2::-1]
                    else:
                        combined_path += finish_visited[link][::-1]
                    logs_queue.put(f"Combined path: {combined_path}")
                    return combined_path, time.time() - start_time, len(start_visited) + len(finish_visited)

    logs_queue.put("Search concluded without finding a path.")
    return None, time.time() - start_time, len(start_visited) + len(finish_visited)

# Exception class remains unchanged
class TimeoutErrorWithLogs(Exception):
    def __init__(self, message, time, discovered):
        super().__init__(message)
        self.time = time
        self.discovered = discovered