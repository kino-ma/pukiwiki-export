import argparse
from argparse import ArgumentParser, Namespace as ArgNamespace
import sys
import tarfile


from html.markdown import Converter
import pukiwiki


def set_args(parser: ArgumentParser):
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=argparse.FileType("wb"),
        default="export.zip",
        help="file name to output zipped export data. Default to"
        "'export.zip`",
    )

    parser.set_defaults(func=main)


def read_tar(tar: tarfile.TarFile) -> Converter:
    print("Start reading tar file...")

    converter = Converter()

    n = len(tar.getmembers())

    for i, member in enumerate(tar):
        i = i + 1
        if not member.isfile():
            continue

        if not pukiwiki.is_wiki_page(member):
            continue

        path = pukiwiki.normalize_path(member.path)

        f = tar.extractfile(member)
        if f is None:
            raise RuntimeError("attempt to extract non-regular file")

        content = f.read()

        prog = f"\rReading file {i:5} / {n:6} ({len(content)} bytes)"
        sys.stdout.write(prog)
        sys.stdout.flush()

        original = pukiwiki.decode(content)
        body = pukiwiki.convert(original)

        converter.append(path, body)

    return converter


def main(parsed_args: ArgNamespace):
    dump_file = parsed_args.pukiwiki_dump

    tar = pukiwiki.open_tar(dump_file)

    converter = read_tar(tar)

    f = parsed_args.output_file
    converter.write_zip(f)
