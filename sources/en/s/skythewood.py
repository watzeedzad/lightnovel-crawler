# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class SkyTheWorld(Crawler):
    base_url = [
        "https://skythewood.blogspot.com/",
    ]
    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        self.init_executor(1)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title.entry-title")
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(soup.select_one(".separator img")["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = "Takibi Amamori (雨森たきび)"
        logger.info("%s", self.novel_author)

        for a in soup.select(".column-center-inner .separator a"):
            if not ("skythewood.blogspot.com") in a["href"]:
                continue
            chap_id = len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        if "Chapter" in soup.select_one("h3").text:
            chapter["title"] = soup.select_one("h3").text

        contents = soup.select_one(".post-body.entry-content")
        return self.cleaner.extract_contents(contents)

    def download_image(self, url: str, headers={}, **kwargs):
        return super().download_image(
            url,
            headers={
                "referer": self.home_url,
                "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            },
            **kwargs
        )
