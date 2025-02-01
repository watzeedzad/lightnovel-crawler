# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class EuricetteCrawler(Crawler):
    base_url = "https://www.euricette.com/"

    def initialize(self) -> None:
        # self.cleaner.bad_css.update(
        #     [
        #         "hr.wp-block-separator",
        #         'span[id^="ezoic-pub-ad"]',
        #     ]
        # )
        self.init_executor(1)
        self.cleaner.bad_text_regex.update(
            [
                "Previous",
                "TOC",
                "Next"
            ]
        )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        # possible_title = soup.select_one("h1.entry-title")
        # assert possible_title, "No title found"
        self.novel_title = "Someday Will I Be The Greatest Alchemist?"

        # cover_img = soup.select_one(".entry-content .wp-block-image img")
        # if cover_img:
        #     src = cover_img.get("data-ezsrc") or cover_img.get("src")
        #     if src:
        self.novel_cover = "https://i.imgur.com/OhKv05D.jpg"

        # first_p = soup.select_one(".inside-article .entry-content > p")
        # if first_p:
        #     t = first_p.get_text(separator="\n", strip=True)
        #     author = next(filter(lambda x: "Author:" in x, t.split("\n")), "")
        self.novel_author = "小狐丸 / KogitsuneMaru"

        for a in soup.select(f'.entry-content a[href^="{self.home_url}"]'):
            if "titles" in self.absolute_url(a["href"]):
                pass
            if "573" in self.absolute_url(a["href"]) or "574" in self.absolute_url(a["href"]):
                pass
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip(),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".entry-content")
        assert contents, "No contents found"
        return self.cleaner.extract_contents(contents)
