from dotenv import load_dotenv
load_dotenv()

import os

from crawler import SimpleCrawler
from cleaner import HtmlCleaner
from embedder import MistralEmbedder
from filter import BoilerplateFilter
from chunker import LangchainChunker
from vectordb import RedisVectorDB

import argparse
from pipeline import IngestionPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")

    args = parser.parse_args()

    api_key = os.getenv('MISTRAL_API_KEY')

    pipeline = IngestionPipeline(
        crawler=SimpleCrawler(),
        cleaner=HtmlCleaner(),
        boilerplate_filter=BoilerplateFilter(),
        chunker=LangchainChunker(),
        embedder=MistralEmbedder(api_key=api_key),
        vectordb=RedisVectorDB()
    )

    pipeline.run(args.url)


if __name__ == "__main__":
    main()