import re

from scrapy import Spider
from scrapy.http import Response
from pathlib import Path


class Crawler(Spider):
    compiled = re.compile(r"\/wiki\/%+(?!(?:[^\"]*\/)*[^\/]+\.svg)\b")
    name = "wiki-spider"
    counter = 0
    base_path = "https://ru.wikipedia.org"
    viewed = set()
    file_to_write = Path("res.txt")


    start_urls = [
        (base_path + "/wiki/%D0%A5%D0%BE%D1%80%D0%B4%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%B3%D1%80%D0%B0%D1%84")
    ]

    def is_valid_page(self, page_link):
        return self.compiled.match(page_link) and page_link not in self.viewed

    def parse(self, response: Response, **kwargs):
        if self.counter > 100:
            self.crawler.engine.close_spider(self, "Достигнуто максимальное количество страниц")

        self.counter += 1
        filename = f"dir/file-{self.counter}.html"
        Path(filename).write_bytes(response.body)
        next_pages = set(filter(self.is_valid_page, response.css("a::attr(href)").getall()))
        self.viewed.update(next_pages)
        with open("res.txt", 'a') as file:
            file.write(f"{self.counter} {response.url}\n")
        yield from response.follow_all(next_pages, callback=self.parse)
