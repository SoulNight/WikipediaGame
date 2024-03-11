import time
import requests
from bs4 import BeautifulSoup
import re
import requests_cache
from threading import Event

# This event will be set when the search should be aborted.
abort_search_event = Event()

# TIMEOUT = 20  # time limit in seconds for the search
TIMEOUT = 1000 # time limit in seconds for the search

# Initialize caching
requests_cache.install_cache('my_cache')

def get_links(page_url):
    # Introduce a delay before making the request
    time.sleep(1)
    # Introduce a delay before making the request
    time.sleep(1)
    print(f"Fetching page: {page_url}")

    response = requests.get(page_url)
    print(f"Finished fetching page: {page_url}")

    soup = BeautifulSoup(response.text, 'html.parser')
    from urllib.parse import urljoin
    all_links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True) if '#' not in a['href']]
    
    # print(f"All links found: {all_links}")
    links = [link for link in all_links if re.match(r'^https://en\.wikipedia\.org/wiki/[^:]*$', link) and '#' not in link]
    print(f"Found {len(links)} links on page: {page_url}")
    return links

def find_path(start_page, finish_page):
    queue = [(start_page, [start_page], 0)]
    discovered = set()
    logs = []
    start_time = time.time()
    while queue:  
        if abort_search_event.is_set():
            # If an abort has been requested, clear the queue to terminate the loop
            logs.append("Search aborted by user request.")
            print("Search aborted by user request.")
            queue.clear()
            return None, logs, time.time() - start_time, len(discovered)

        (vertex, path, depth) = queue.pop(0)
        for next in set(get_links(vertex)) - discovered:
            if abort_search_event.is_set():
                # Check for abort signal again before processing the next link
                logs.append("Search aborted by user request.")
                print("Search aborted by user request.")
                queue.clear()
                return None, logs, time.time() - start_time, len(discovered)
                
            if next == finish_page:
                log = f"Found finish page: {next}"
                print(log)
                logs.append(log)
                elapsed_time = time.time() - start_time
                logs.append(f"Search took {elapsed_time} seconds.")
                logs.append(f"Discovered pages: {len(discovered)}")
                return path + [next], logs, elapsed_time, len(discovered)
            else:
                log = f"Adding link to queue: {next} (depth {depth})"
                print(log)
                logs.append(log)
                discovered.add(next)
                queue.append((next, path + [next], depth + 1))
        # The timeout check has been removed since you will control the timeout externally now
    logs.append("Search concluded without finding the finish page.")
    return None, logs, time.time() - start_time, len(discovered)

class TimeoutErrorWithLogs(Exception):
    def __init__(self, message, logs, time, discovered):
        super().__init__(message)
        self.logs = logs
        self.time = time
        self.discovered = discovered
