import argparse
from argparse import ArgumentParser, Namespace as ArgNamespace

import json
import tarfile
import typing
import zipfile
from typing import Tuple

import pukiwiki
from growi.date import now_iso
from growi.page import Page
from growi.revision import Revision
from growi.user import User
from growi.password import random_seed


EUC_JP_SLASH = "2F"
FILE_SUFFIX = ".txt"

META_JSON = "meta.json"
PAGES_JSON = "pages.json"
REVISIONS_JSON = "revisions.json"
USERS_JSON = "users.json"

DEFAULT_RGOWI_VERSION = "5.0.2"


def set_args(parser: ArgumentParser):
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

    parser.set_defaults


def create_page(tarinfo: tarfile.TarInfo, path_prefix: str):
    if not tarinfo.isfile():
        raise RuntimeError("Given TarInfo was not a file")

    path = tarinfo.path
    path = pukiwiki.normalize_path(path, path_prefix)

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
    original = pukiwiki.decode(content)
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


def get_users_json_from_user(user: User) -> list[dict]:
    d = [user.json()]
    return d


def get_users_json(password_seed: str, name: str = "pukiwiki") -> list[dict]:
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
) -> Tuple[list[dict], list[dict]]:
    """Returns three dictionary, pages.json, revisions.json"""

    pages = []
    revisions = []

    for member in tar_file:
        if not member.isfile():
            continue

        if not pukiwiki.is_wiki_page(member):
            print("skipping", member.path)
            continue

        page = create_page(member, path_prefix)
        revision = create_revision(tar_file, member, page, user)
        page.revisionId = revision.id

        p = page.json()
        pages.append(p)
        r = revision.json()
        revisions.append(r)

    return pages, revisions


def write_zip(
    file: typing.IO[bytes],
    pages: list[dict],
    revisions: list[dict],
    users: list[dict],
    meta: dict,
    pages_filename: str = PAGES_JSON,
    revisions_filename: str = REVISIONS_JSON,
    users_filename: str = USERS_JSON,
    meta_filename: str = META_JSON,
):
    with zipfile.ZipFile(file, "x") as f:
        p = json.dumps(pages)
        f.writestr(pages_filename, p)

        r = json.dumps(revisions)
        f.writestr(revisions_filename, r)

        u = json.dumps(users)
        f.writestr(users_filename, u)

        m = json.dumps(meta)
        f.writestr(meta_filename, m)


def main(parsed_args: ArgNamespace):
    dump_file = parsed_args.pukiwiki_dump

    output_file = parsed_args.output_file
    prefix = parsed_args.prefix
    user_name = parsed_args.name
    growi_version = parsed_args.growi_version

    password_seed = random_seed()
    meta = get_meta_json(password_seed, growi_version)
    user = create_user(password_seed, user_name)
    users = get_users_json_from_user(user)

    tar = pukiwiki.open_tar(dump_file)
    pages, revisions = get_data_json(tar, prefix, user)

    write_zip(output_file, pages, revisions, users, meta)
