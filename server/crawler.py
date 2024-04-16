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
            return None, time.time() - start_time, len(discovered), 'breadth-first'

        (vertex, path) = queue.pop(0)
        for next in set(get_links(vertex, logs_queue)) - discovered:
            if next == finish_page:
                logs_queue.put(f"Found finish page: {next}")
                return path + [next], time.time() - start_time, len(discovered), 'breadth-first'
            discovered.add(next)
            queue.append((next, path + [next]))

    logs_queue.put("Search concluded without finding the finish page.")
    return None, time.time() - start_time, len(discovered), 'breadth-first'

def bidirectional_search(start_page, finish_page, logs_queue):
    if start_page == finish_page:
        logs_queue.put("Start and finish pages are the same.")
        return [start_page], 0, 1, 'bidirectional'

    start_queue = [(start_page, [start_page])]
    finish_queue = [(finish_page, [finish_page])]
    start_visited = {start_page: [start_page]}
    finish_visited = {finish_page: [finish_page]}
    start_time = time.time()

    while start_queue and finish_queue:
        if abort_search_event.is_set():
            logs_queue.put("Search aborted by user request.")
            return None, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional'
        
        # Expand from the start side
        current_start, path_start = start_queue.pop(0)
        start_links = get_links(current_start, logs_queue)
        for link in start_links:
            if link not in start_visited:
                start_visited[link] = path_start + [link]
                start_queue.append((link, start_visited[link]))
                if link in finish_visited:
                    logs_queue.put(f"Path found connecting through: {link}")
                    # Combine paths while avoiding duplicating the connecting link
                    combined_path = start_visited[link][:-1] if start_visited[link][-1] == link else start_visited[link]
                    combined_path += finish_visited[link][::-1]
                    return combined_path, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional'

        # Expand from the finish side
        current_finish, path_finish = finish_queue.pop(0)
        finish_links = get_links(current_finish, logs_queue)
        for link in finish_links:
            if link not in finish_visited:
                finish_visited[link] = path_finish + [link]
                finish_queue.append((link, finish_visited[link]))
                if link in start_visited:
                    logs_queue.put(f"Path found connecting through: {link}")
                    # Combine paths while avoiding duplicating the connecting link
                    combined_path = finish_visited[link][:-1] if finish_visited[link][-1] == link else finish_visited[link]
                    combined_path += start_visited[link][::-1]
                    return combined_path[::-1], time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional'

    logs_queue.put("Search concluded without finding a path.")
    return None, time.time() - start_time, len(start_visited) + len(finish_visited), 'bidirectional'


def depth_first_search(start_page, finish_page, logs_queue):
    stack = [(start_page, [start_page])]
    discovered = set([start_page])
    start_time = time.time()

    while stack:
        if abort_search_event.is_set():
            logs_queue.put("Search aborted by user request.")
            return None, time.time() - start_time, len(discovered), 'depth-first'

        (vertex, path) = stack.pop()
        if vertex == finish_page:
            logs_queue.put(f"Found finish page: {vertex}")
            return path, time.time() - start_time, len(discovered), 'depth-first'

        for next_link in set(get_links(vertex, logs_queue)) - discovered:
            if abort_search_event.is_set():
                logs_queue.put("Search aborted by user request.")
                return None, time.time() - start_time, len(discovered), 'depth-first'
            discovered.add(next_link)
            stack.append((next_link, path + [next_link]))

    logs_queue.put("Search concluded without finding the finish page.")
    return None, time.time() - start_time, len(discovered), 'depth-first'
