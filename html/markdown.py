import pandoc

_PANDOC_FORMAT_MARKDOWN = "markdown"
_PANDOC_FORMAT_HTML = "html"


def to_html(markdown: str) -> str:
    doc = pandoc.read(markdown, format=_PANDOC_FORMAT_MARKDOWN)
    return pandoc.write(doc, format=_PANDOC_FORMAT_HTML)


if __name__ == "__main__":
    print(to_html("# Hello World!"))
