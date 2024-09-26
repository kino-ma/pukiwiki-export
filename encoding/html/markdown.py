import os
from typing import IO
import zipfile

import pandoc

from encoding.html.page import Page

_PANDOC_FORMAT_MARKDOWN = "markdown"
_PANDOC_FORMAT_HTML = "html"


def possible_paths(paths: list[str]) -> list[str]:
    if len(paths) <= 1:
        return paths

    me = paths[0]
    children = possible_paths(paths[1:])

    out = [me]

    for child in children:
        path = os.path.join(me, child)
        out.append(path)

    return out


class Converter:
    results: dict[str, Page]

    def __init__(self):
        self.results = {}

    def append(self, path: str, markdown: str) -> Page:
        page = self.parse(path, markdown)

        parents = self.find_parent_path(page.path)
        for p in parents:
            parent_page = self.results[p]
            del self.results[p]

            new_page = parent_page.to_index()
            self.results[new_page] = new_page

        self.results[path] = page

        return page

    def find_parent_path(self, path: str) -> list[str]:
        parents = []
        paths = list(os.path.split(path))
        possible_parents = possible_paths(paths)

        for p in possible_parents:
            if self.results.get(p) is not None:
                parents.append(p)

        return parents

    def write_zip(self, file: IO[bytes]):
        with zipfile.ZipFile(file, "x") as f:
            for page in self.results.values():
                self.write_page(f, page)

    def write_page(self, zip: zipfile.ZipFile, page: Page):
        content = pandoc.write(
            page.doc, format=_PANDOC_FORMAT_HTML, options=["-s"]
        )
        path = page.path
        zip.writestr(path, content)

    @classmethod
    def parse(_cls, path: str, markdown: str) -> Page:
        doc = pandoc.read(markdown, format=_PANDOC_FORMAT_MARKDOWN)
        return Page(path, doc)
