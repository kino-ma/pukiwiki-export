import argparse
from argparse import ArgumentParser, Namespace as ArgNamespace
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

    parser.set_defaults


def read_tar(tar: tarfile.TarFile) -> Converter:
    converter = Converter()

    for member in tar:
        if not member.isfile():
            continue

        if not pukiwiki.is_wiki_page(member):
            print("skipping", member.path)
            continue

        path = pukiwiki.normalize_path(member.path)

        f = tar.extractfile(member)
        if f is None:
            raise RuntimeError("attempt to extract non-regular file")

        content = f.read()
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
