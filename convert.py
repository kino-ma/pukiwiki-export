#!/usr/bin/env pytohn3

import urllib.parse
import argparse
import sys


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Convert Pukiwiki formatted text data into Growi importable zipped file."
    )

    parser.add_argument(
        "pukiwiki_dump",
        metavar="DUMP_FILE",
        type=argparse.FileType("r"),
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


def main():
    args = parse_args(sys.argv[1:])

    dump_file = args.pukiwiki_dump
    output_file = args.output_file
    prefix = args.prefix

    print(dump_file, output_file, prefix)


if __name__ == "__main__":
    main()
