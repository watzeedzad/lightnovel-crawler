import logging

from bs4 import BeautifulSoup, Tag

from lncrawl.core.exeptions import FallbackToBrowser
from lncrawl.models import Chapter
from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class ToonHunter(MangaStreamTemplate):
    has_mtl = False
    has_manga = True
    base_url = ["https://toonhunter.com/", "https://doujin89.com/"]

    def initialize(self) -> None:
        self.init_executor(1)

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        contents = soup.select_one("#readerarea")

        for img in contents.findAll("img"):
            if img.has_attr("data-src"):
                src_url = img["data-src"]
                parent = img.parent
                img.extract()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        clean_contents = self.cleaner.clean_contents(contents)
        return clean_contents

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        raise FallbackToBrowser()
