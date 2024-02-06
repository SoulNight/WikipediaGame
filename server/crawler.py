import time
import requests
from bs4 import BeautifulSoup

import re

def get_links(page_url):
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

    # breadth first search
    start_time = time.time()
    while queue and time.time() - start_time < 30:  # 30 seconds time limit
        elapsed_time = time.time() - start_time
        if elapsed_time >= 30:
            logs.append(f"Search took too long ({elapsed_time} seconds). Time limit exceeded.")
        (vertex, path, depth) = queue.pop(0)
        for next in set(get_links(vertex)) - discovered:
            if next == finish_page:
                log = f"Found finish page: {next}"
                print(log)
                logs.append(log)
                elapsed_time = time.time() - start_time
                logs.append(f"Search took {elapsed_time} seconds.")
                return path + [next], logs
            else:
                log = f"Adding link to visited: {next} (depth {depth})"
                print(log)
                logs.append(log)
                discovered.add(next)
                queue.append((next, path + [next], depth + 1))
    elapsed_time = time.time() - start_time
    logs.append(f"Search took {elapsed_time} seconds.")
    return [], logs
