import re


def get_date(src) -> str | None:
    m = re.match(r'^#author\("(.*)",".*",".*"\)', src)

    if m is None:
        return None

    date = m.group(1)
    if date == "":
        return None

    return date


def _sub(pattern, repl, string, count=0, flags=0):
    s = re.sub(pattern, repl, string, count=count, flags=re.MULTILINE | flags)
    return s


def delete_hash(src):
    s = _sub(r" \[#[0-9a-z]+\]$", "", src)
    return s


def convert_bullets(src):
    s1 = _sub(r"^---", "        -", src)
    s2 = _sub(r"^--", "    -", s1)
    s3 = _sub(r"^(\s*)-([^ ])", r"\1- \2", s2)

    return s3


def convert_br(src):
    s = _sub(r"&br", "<br>", src)
    return s


def convert_pre(src):
    s1 = _sub(r"^#pre{*", "```", src)
    s2 = _sub(r"^}}*", "```", s1)

    return s2


def convert_strike(src):
    s = _sub(r"%%", "~~", src)

    return s


def convert_lsx(src):
    s = _sub(r"^\#lsx", r"$lsx()", src)

    return s


def convert_headings(src):
    "Because other notations also use `#`, this conversion must be run at the last"
    s1 = _sub(r"^\*\*\*", "###", src)
    s2 = _sub(r"^\*\*", "##", s1)
    s3 = _sub(r"^\*", "#", s2)
    s4 = _sub(r"^(#+)([^ #])", r"\1 \2", s3)

    return s4


def convert(src):
    funcs = [
        delete_hash,
        convert_bullets,
        convert_br,
        convert_pre,
        convert_strike,
        convert_lsx,
        convert_headings,
    ]

    s = src
    for f in funcs:
        s = f(s)

    return s


def _run_convert_test():
    text = r"""hoge [#fuga]
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
