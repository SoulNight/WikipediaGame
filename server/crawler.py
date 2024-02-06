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
    visited = set()
    logs = []

    import time

    start_time = time.time()
    while queue and time.time() - start_time < 30:  # 30 seconds time limit
        (vertex, path, depth) = queue.pop(0)
        for next in set(get_links(vertex)) - visited:
            log = f"Following link: {next} (depth {depth})"
            print(log)
            logs.append(log)
            if next == finish_page:
                log = f"Found finish page: {next}"
                print(log)
                logs.append(log)
                return path + [next], logs
            else:
                log = f"Adding link to queue: {next}"
                print(log)
                logs.append(log)
                visited.add(next)
                queue.append((next, path + [next], depth + 1))
    return [], logs
