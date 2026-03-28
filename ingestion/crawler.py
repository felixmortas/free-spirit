import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class SimpleCrawler:
    def __init__(self, max_pages=100):
        self.max_pages = max_pages

    def crawl(self, start_url: str):
        visited = set()
        to_visit = [start_url]
        domain = urlparse(start_url).netloc
        results = []

        while to_visit and len(visited) < self.max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue

            try:
                res = requests.get(url, timeout=5)
                html = res.text
            except Exception:
                continue

            visited.add(url)
            results.append((url, html))

            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if urlparse(link).netloc == domain:
                    to_visit.append(link)

        return results