import html
import os
import re
import tarfile
import urllib.parse

_pat_author = re.compile(r'^#author\("(.*)","(.*)","(.*)"\)\n?')
two_chars = re.compile("..?")

DEFAULT_ENCODING = "euc_jp"


def open_tar(file):
    tar = tarfile.TarFile(fileobj=file, encoding=DEFAULT_ENCODING)
    return tar


def get_date(src) -> str | None:
    m = re.match(_pat_author, src)

    if m is None:
        return None

    date = m.group(1)
    if date == "":
        return None

    return date


def _sub(pattern, repl, string, count=0, flags=0):
    s = re.sub(pattern, repl, string, count=count, flags=re.MULTILINE | flags)
    return s


def delete_author(src):
    s = re.sub(_pat_author, "", src)
    return s


def delete_hash(src):
    s = _sub(r" \[#[0-9a-z]+\]$", "", src)
    return s


def delete_toc(src):
    s = _sub(r"^#contents", "", src)
    return s


def convert_link(src: str):
    # Replace the alias notation
    replaced = src.replace(">", ":")
    out = replaced

    # Start iteration from the tail of the string as the matching index will shift as we replace the substrings
    for match in reversed(
        list(re.finditer(r"(?<=\[\[)(.+)(?=\]\])", replaced))
    ):
        group = match.group()
        parts = group.split(":", maxsplit=1)

        # This is internal wiki link. Keep original text
        if len(parts) <= 1:
            continue

        name, url = parts

        parsed = urllib.parse.urlparse(url)

        # This is InterWiki link. Keep original text
        if parsed.netloc == "":
            continue

        # Then this is external web link!

        # If the link has no name
        if parsed.scheme == "":
            name = url = group

        md = f"[{name}]({url})"

        # Include [[ and ]]
        start, end = match.start() - 2, match.end() + 2
        out = out[:start] + md + out[end:]

    return out


def convert_bullets(src):
    s1 = _sub(r"^---", "        -", src)
    s2 = _sub(r"^--", "    -", s1)
    s3 = _sub(r"^(\s*)-([^ ])", r"\1- \2", s2)

    return s3


def convert_br(src):
    s = _sub(r"&br", "  ", src)
    return s


def convert_pre(src):
    s1 = _sub(r"^#pre{*", "```", src)
    s2 = _sub(r"^}}*", "```", s1)

    return s2


def convert_strike(src):
    s = _sub(r"%%", "~~", src)

    return s


def convert_strong(src):
    s = _sub(r"''", "**", src)

    return s


def convert_emphasis(src):
    s = _sub(r"'''", "*", src)

    return s


def convert_lsx(src):
    s = _sub(r"^\#lsx", r"$lsx()", src)

    return s


def convert_headings(src):
    """Because other notations also use `#`, this conversion must be run at the
    last"""
    s1 = _sub(r"^\*\*\*", "###", src)
    s2 = _sub(r"^\*\*", "##", s1)
    s3 = _sub(r"^\*", "#", s2)
    s4 = _sub(r"^(#+)([^ #])", r"\1 \2", s3)

    return s4


def convert_codeblock(src: str):
    lines = src.split("\n")

    start, end = None, None
    starts = []
    ends = []

    for i, line in enumerate(lines):
        # We find a code block
        if line.startswith(" "):
            # trim space
            lines[i] = line[1:]

            # If the first line of code block
            if start is None:
                start = i

            # Continue reading code block
            elif line.startswith(" ") and start is not None:
                continue

        # End reading code block
        elif not line.startswith(" ") and start is not None:
            starts.append(start)
            ends.append(i)
            start, end = None, None
        else:
            continue

    # Iterate from end of the list.
    # Because we are inserting new elements and alder indeices will be destroyed.
    for start, end in list(zip(starts, ends))[::-1]:
        lines.insert(end, "```")
        lines.insert(start, "```")

    return "\n".join(lines)


def sanitize_html(src):
    s = html.escape(src)
    return s


def convert(src):
    funcs = [
        delete_author,
        delete_hash,
        delete_toc,
        convert_link,
        convert_bullets,
        convert_br,
        convert_pre,
        convert_strike,
        convert_strong,
        convert_emphasis,
        convert_lsx,
        convert_headings,
        convert_codeblock,
        sanitize_html,
    ]

    s = src
    for f in funcs:
        s = f(s)

    return s


def decode(
    content: bytes, encoding=DEFAULT_ENCODING, errors="backslashreplace"
) -> str:
    return content.decode(encoding, errors=errors)


def to_url_encode(s: str) -> str:
    matches = two_chars.findall(s)
    matches.insert(0, "")
    encoded = "%".join(matches)
    return encoded


def decode_path(path: str) -> str:
    url_encoded = to_url_encode(path)
    decoded = urllib.parse.unquote(url_encoded, encoding=DEFAULT_ENCODING)
    return decoded


def normalize_path(path: str, prefix: str = "") -> str:
    path = os.path.basename(path)
    path, _ = os.path.splitext(path)
    path = decode_path(path)

    if prefix != "":
        path = os.path.join(prefix, path)

    return path


def is_wiki_page(tarinfo: tarfile.TarInfo) -> bool:
    is_wiki_prefix = tarinfo.path.startswith(
        "wiki/"
    ) or tarinfo.path.startswith("/wiki/")

    path = normalize_path(tarinfo.path)
    name = os.path.split(path)[-1]
    is_special_page = name.startswith(":")

    return is_wiki_prefix and not is_special_page


def _run_convert_test():
    text = r"""#author("2018-11-08T16:04:27+09:00","","")
hoge [#fuga]
***hoge
**fuga
*piyo
-hoge
--fuga
---piyo
&br
#pre{
    hoge
}
#pre{{
fuga
hogefuga
}}
%%hegu%%
#lsx
"""

    want = r"""hoge
### hoge
## fuga
# piyo
- hoge
    - fuga
        - piyo
<br>
```
    hoge
```
```
fuga
hogefuga
```
~~hegu~~
$lsx()
"""

    got = convert(text)
    if want == got:
        print("ok")
    else:
        print("failed")
        print("=== want ===")
        print(want)
        print("=== got ===")
        print(got)
        print("=== end ===")


def _run_date_test():
    text1 = """#author("2018-11-08T16:04:27+09:00","","")"""
    want1 = "2018-11-08T16:04:27+09:00"

    got1 = get_date(text1)
    if want1 == got1:
        print("ok")
    else:
        print("failed")
        print("=== want ===")
        print(want1)
        print("=== got ===")
        print(got1)
        print("=== end ===")

    text2 = """#author("2022-06-28T08:46:56+00:00","default:ht","ht")"""
    want2 = "2022-06-28T08:46:56+00:00"

    got2 = get_date(text2)
    if want2 == got2:
        print("ok")
    else:
        print("failed")
        print("=== want ===")
        print(want2)
        print("=== got ===")
        print(got2)
        print("=== end ===")

    text3 = """#author("","default:ht","ht")"""
    want3 = None

    got3 = get_date(text3)
    if want3 == got3:
        print("ok")
    else:
        print("failed")
        print("=== want ===")
        print(want3)
        print("=== got ===")
        print(got3)
        print("=== end ===")


if __name__ == "__main__":
    _run_convert_test()
    _run_date_test()
