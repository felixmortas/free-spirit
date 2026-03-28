import os

class IngestionPipeline:
    def __init__(self, crawler, cleaner, boilerplate_filter, chunker, embedder, vectordb):
        self.crawler = crawler
        self.cleaner = cleaner
        self.boilerplate_filter = boilerplate_filter
        self.chunker = chunker
        self.embedder = embedder
        self.vectordb = vectordb

        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/clean", exist_ok=True)

    def run(self, url: str):
        # Crawl website pages
        pages = self.crawler.crawl(url)

        # Clean pages to keep minimal usefull text
        cleaned_pages = []
        for i, (page_url, html) in enumerate(pages):
            with open(f"data/raw/page_{i}.html", "w", encoding="utf-8") as f:
                f.write(html)

            clean_text = self.cleaner.clean(html)

            first_line = clean_text.splitlines()[0] if clean_text else ""
            if "ecuador" not in first_line.lower():
                continue  # ← on ne produit pas le .txt

            with open(f"data/clean/page_{i}.txt", "w", encoding="utf-8") as f:
                f.write(clean_text)

            cleaned_pages.append((page_url, clean_text))

        # Merge pages and remove duplicated lines between pages
        merged_text = self.boilerplate_filter.filter(cleaned_pages)
        with open("data/merged.txt", "w", encoding="utf-8") as f:
            f.write(merged_text)

        # Chunk the merged text
        chunks = self.chunker.split(merged_text)

        # Vectorise the chunks
        vectors = self.embedder.embed(chunks)

        self.vectordb.add(chunks, vectors)
