import pandoc

_PANDOC_FORMAT_MARKDOWN = "markdown"


def to_html(markdown: str) -> str:
    doc = pandoc.read(markdown, format=_PANDOC_FORMAT_MARKDOWN)

    print(type(doc))
    print(doc)

    return ""


if __name__ == "__main__":
    to_html("# Hello World!")
