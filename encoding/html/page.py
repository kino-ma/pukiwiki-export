import os

from pandoc.types import Pandoc

_INDEX_FILENAME = "index"


class Page:
    path: str
    doc: Pandoc

    def __init__(self, path: str, doc: Pandoc):
        self.path = path
        self.doc = doc

    def to_index(self) -> "Page":
        path = os.path.join(self.path, _INDEX_FILENAME)
        return Page(path, self.doc)
