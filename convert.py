#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
import tarfile
import urllib.parse
from typing import Tuple

from lib import pukiwiki
from lib.page import Page
from lib.revision import Revision


DEFAULT_ENCODING = "euc_jp"
EUC_JP_SLASH = "2F"
FILE_SUFFIX = ".txt"


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Convert Pukiwiki formatted text data into Growi"
        "importable zipped file."
    )

    parser.add_argument(
        "pukiwiki_dump",
        metavar="DUMP_FILE",
        type=argparse.FileType("rb"),
        help="pukiwiki dump file (tar.gz)",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="file name to output zipped export data",
    )

    parser.add_argument(
        "-p",
        "--path-prefix",
        dest="prefix",
        type=str,
        required=False,
        default="pukiwiki",
        help="path prefix to be inserted to output pages. default to 'pukiwiki"
        "'.",
    )

    parsed_args = parser.parse_args(args)
    return parsed_args


def open_tar(file):
    tar = tarfile.TarFile(fileobj=file, encoding=DEFAULT_ENCODING)
    return tar


two_chars = re.compile("..?")


def to_url_encode(s: str) -> str:
    matches = two_chars.findall(s)
    matches.insert(0, "")
    encoded = "%".join(matches)
    return encoded


def decode_path(path: str) -> str:
    url_encoded = to_url_encode(path)
    decoded = urllib.parse.unquote(url_encoded, encoding=DEFAULT_ENCODING)
    return decoded


def normalize_path(path: str, prefix: str) -> str:
    path = os.path.basename(path)
    path, _ = os.path.splitext(path)
    path = decode_path(path)
    path = os.path.join(prefix, path)
    return path


def create_page(tarinfo: tarfile.TarInfo, path_prefix: str):
    if not tarinfo.isfile():
        raise RuntimeError("Given TarInfo was not a file")

    path = tarinfo.path
    path = normalize_path(path, path_prefix)

    page = Page(path)

    return page


def create_revision(
    tar: tarfile.TarFile, member: tarfile.TarInfo, page: Page
) -> Revision:
    f = tar.extractfile(member)

    if f is None:
        raise RuntimeError("attempt to extract non-regular file")

    content = f.read()
    original = content.decode(DEFAULT_ENCODING, errors="backslashreplace")
    body = pukiwiki.convert(original)

    date = pukiwiki.get_date(original)
    date = date or page.createdAt

    revision = Revision(page.id, body, createdAt=date)

    page.revisionId = revision.id
    if date is not None:
        page.createdAt = page.updatedAt = date

    return revision


def get_json(tar_file: tarfile.TarFile, path_prefix: str) -> Tuple[dict, dict]:
    """Returns two dictionary, pages.json and revisions.json"""

    pages = []
    revisions = []

    for member in tar_file:
        if not member.isfile():
            continue

        page = create_page(member, path_prefix)
        revision = create_revision(tar_file, member, page)

        p = page.json()
        pages.append(p)
        r = revision.json()
        revisions.append(r)

    return (pages, revisions)


def main():
    args = parse_args(sys.argv[1:])

    dump_file = args.pukiwiki_dump
    output_file = args.output_file
    prefix = args.prefix

    tar = open_tar(dump_file)
    pages, revisions = get_json(tar, prefix)

    print(json.dumps(revisions), file=output_file)


if __name__ == "__main__":
    main()
