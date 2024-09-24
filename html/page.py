from pandoc.types import Pandoc


class Page:
    path: str
    doc: Pandoc

    def __init__(self, path: str, doc: Pandoc):
        self.path = path
        self.doc = doc
