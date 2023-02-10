#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tarfile
import urllib.parse

from lib.page import Page


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Convert Pukiwiki formatted text data into Growi importable zipped file."
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
        required=True,
        help="file name to output zipped export data",
    )

    parser.add_argument(
        "-p",
        "--path-prefix",
        dest="prefix",
        type=str,
        required=False,
        default="pukiwiki",
        help="path prefix to be inserted to output pages. default to 'pukiwiki'.",
    )

    parsed_args = parser.parse_args(args)
    return parsed_args


def open_tar(file):
    tar = tarfile.TarFile(fileobj=file)
    return tar


def convert_page(tarinfo: tarfile.TarInfo, path_prefix: str):
    if not tarinfo.isfile():
        raise RuntimeError("Given TarInfo was not a file")

    time = tarinfo.mtime

    path = tarinfo.path
    path = os.path.join(path_prefix, path)

    page = Page(path, createdAt=time, updatedAt=time)

    return page


def pages_json(tar_file: tarfile.TarFile, path_prefix: str):
    data = []

    for member in tar_file:
        if not member.isfile():
            continue

        page = convert_page(member, path_prefix)

        d = page.json()
        data.append(d)

    return data


def main():
    args = parse_args(sys.argv[1:])

    dump_file = args.pukiwiki_dump
    output_file = args.output_file
    prefix = args.prefix

    tar = open_tar(dump_file)
    data = pages_json(tar, prefix)

    print(json.dumps(data))


if __name__ == "__main__":
    main()
