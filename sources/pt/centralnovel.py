# -*- coding: utf-8 -*-
import logging

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter
from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class CentralNovelCrawler(MangaStreamTemplate):
    has_manga = True
    has_novel = False

    base_url = ["https://www.godhman.net/"]

    def initialize(self) -> None:
        self.init_executor(1, ratelimit=1.1)

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("#readerarea")

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)
        body = self.select_chapter_body(soup)
        return self.cleaner.extract_contents(body)
