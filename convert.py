#!/usr/bin/env python3

import argparse
import io
import json
import os
import re
import sys
import tarfile
import urllib.parse
import zipfile
from typing import Tuple

from lib import pukiwiki
from lib.date import now_iso
from lib.page import Page
from lib.password import random_seed
from lib.revision import Revision
from lib.user import User


DEFAULT_ENCODING = "euc_jp"
EUC_JP_SLASH = "2F"
FILE_SUFFIX = ".txt"

META_JSON = "meta.json"
PAGES_JSON = "pages.json"
REVISIONS_JSON = "revisions.json"
USERS_JSON = "users.json"

DEFAULT_RGOWI_VERSION = "5.0.2"


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
        type=argparse.FileType("wb"),
        default="export.growi.zip",
        help="file name to output zipped export data. Default to"
        "'export.growi.zip`",
    )

    parser.add_argument(
        "-p",
        "--path-prefix",
        dest="prefix",
        type=str,
        required=False,
        default="pukiwiki",
        help="path prefix to be inserted to output pages. Default to 'pukiwiki"
        "'.",
    )

    parser.add_argument(
        "-u",
        "--user-name",
        dest="name",
        type=str,
        required=False,
        default="pukiwiki",
        help="an user's name to be set as a author of exported pages.",
    )

    parser.add_argument(
        "-g",
        "--growi-version",
        dest="growi_version",
        type=str,
        required=False,
        default="5.0.2",
        help="version of the destination Growi server. Default to 5.0.2",
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
    tar: tarfile.TarFile,
    member: tarfile.TarInfo,
    page: Page,
    author: User,
) -> Revision:
    f = tar.extractfile(member)

    if f is None:
        raise RuntimeError("attempt to extract non-regular file")

    content = f.read()
    original = content.decode(DEFAULT_ENCODING, errors="backslashreplace")
    body = pukiwiki.convert(original)

    date = pukiwiki.get_date(original)
    date = date or page.createdAt

    revision = Revision(
        page.id,
        body,
        author.id,
        createdAt=date,
    )

    page.revisionId = revision.id
    if date is not None:
        page.createdAt = page.updatedAt = date

    return revision


def create_user(password_seed: str, name: str = "pukiwiki") -> User:
    user = User(name, password_seed)
    return user


def get_users_json_from_user(user: User) -> dict:
    d = [user.json()]
    return d


def get_users_json(password_seed: str, name: str = "pukiwiki"):
    user = create_user(password_seed, name)
    d = get_users_json_from_user(user)
    return d


def get_meta_json(
    password_seed: str, version=DEFAULT_RGOWI_VERSION, exported_at=now_iso()
):
    d = {
        "version": version,
        "passwordSeed": password_seed,
        "exportedAt": exported_at,
    }
    return d


def get_data_json(
    tar_file: tarfile.TarFile, path_prefix: str, user: User
) -> Tuple[dict, dict, dict]:
    """Returns three dictionary, pages.json, revisions.json, and meta.json"""

    pages = []
    revisions = []

    for member in tar_file:
        if not member.isfile():
            continue

        page = create_page(member, path_prefix)
        revision = create_revision(tar_file, member, page, user)

        p = page.json()
        pages.append(p)
        r = revision.json()
        revisions.append(r)

    return pages, revisions


def write_zip(
    file: io.BufferedWriter,
    pages: dict,
    revisions: dict,
    users: dict,
    meta: dict,
    pages_filename: str = PAGES_JSON,
    revisions_filename: str = REVISIONS_JSON,
    users_filename: str = USERS_JSON,
    meta_filename: str = META_JSON,
):
    with zipfile.ZipFile(file, "x") as file:
        p = json.dumps(pages)
        file.writestr(pages_filename, p)

        r = json.dumps(revisions)
        file.writestr(revisions_filename, r)

        u = json.dumps(users)
        file.writestr(users_filename, u)

        m = json.dumps(meta)
        file.writestr(meta_filename, m)


def main():
    args = parse_args(sys.argv[1:])

    dump_file = args.pukiwiki_dump
    output_file = args.output_file
    prefix = args.prefix
    user_name = args.name
    growi_version = args.growi_version

    password_seed = random_seed()
    meta = get_meta_json(password_seed, growi_version)
    user = create_user(password_seed, user_name)
    users = get_users_json_from_user(user)

    tar = open_tar(dump_file)
    pages, revisions = get_data_json(tar, prefix, user)

    write_zip(output_file, pages, revisions, users, meta)


if __name__ == "__main__":
    main()
