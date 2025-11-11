#!/usr/bin/env python3
import webdav3.exceptions
from webdav3.client import Client
from datetime import datetime
from pathlib import Path
import exifread
import yaml
import re


class CannotParseFilename(Exception):
    pass

class CannotParseEXIF(Exception):
    pass

class DifferentFileAlreadyExists(Exception):
    pass



def get_month_from_filename(client, info):
    m = re.match(r"[^\d]*(20[012]\d)(\d\d)\d\d.*", info["fname"])
    if m:
        return (m.group(1), m.group(2))
    m = re.match(r".*(20[0123]\d)-(\d\d)[^\d].*", info["fname"])
    if m:
        return (m.group(1), m.group(2))


def get_month_from_EXIF(client, info):
    client.download_sync(remote_path=info["relative_path"], local_path="/tmp/local")
    local_path = Path("/tmp/local")
    tags = exifread.process_file(local_path.open('rb'))
    if "EXIF DateTimeOriginal" not in tags:
        return
    date_obj = datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
    return (str(date_obj.year), f"{date_obj.month:02d}")


credentials_file = Path("/secret/credentials")
options = yaml.safe_load(credentials_file.read_text())
client = Client(options)
root_part = len(client.webdav.root)

def save_file(client, info, year, month):
    client.mkdir(f"/Photos/{year}")
    client.mkdir(f"/Photos/{year}/{month}")
    try:
        existing_file = client.info(f"/Photos/{year}/{month}/{info['fname']}")
    except webdav3.exceptions.RemoteResourceNotFound:
        existing_file = None

    if existing_file:
        print(f"File already exists! existing_file={existing_file}")
    if existing_file is None or existing_file["size"] < info["size"]:
        print(
            f"Moving {info['relative_path']} to /Photos/{year}/{month}/{info['fname']}"
        )
        client.move(
            remote_path_from=info["relative_path"],
            remote_path_to=f"/Photos/{year}/{month}/{info['fname']}",
            overwrite=True,
        )
    else:
        print(f"Removing {info['relative_path']}")
        client.clean(info["relative_path"])
    return

def walker(client, path):
    for info in client.list(path, get_info=True):
        info["relative_path"] = info["path"][root_part:]
        info["fname"] = info["path"].split("/")[-1]
        print(f"info={info}")

        if info["isdir"]:
            try:
                walker(client, info['relative_path'])
            except webdav3.exceptions.RemoteResourceNotFound:
                print(f"Cannot walk in {info['relative_path']}")
                pass
        elif info["fname"].startswith(".trashed"):
          print(f"trashed file: skipping")
        elif int(info["size"]) < 100 * 1024:
          print(f"To small: skipping")
        elif date := get_month_from_filename(client, info):
            year, month = date
            print(f"From filename -> year={year} month={month}")
            save_file(client, info, year, month)
        elif date := get_month_from_EXIF(client, info):
            year, month = date
            print(f"From EXIF -> year={year} month={month}")
            save_file(client, info, year, month)
walker(client, "Photos/a_trier")
