# -*- coding: utf-8 -*-

from lncrawl.templates.novelpub import NovelPubTemplate


class LightnovelworldComCrawler(NovelPubTemplate):
    base_url = [
        "https://www.lightnovelworld.com/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)
