#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2018-2019 Mohamed El Morabity
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


import contextlib
from enum import Enum
import ftplib
import hashlib
import os
import tempfile
import time

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.utils.path import makedirs_safe


DOCUMENTATION = """
---
module: ftp
author: Mohamed El Morabity
short_description: Transfers files and directories from or to FTP servers
description:
  - Transfers files and directories from or to FTP servers.
options:
  host:
    description:
      - FTP server.
    required: True
  port:
    description:
      - FTP port.
    type: int
    required: False
    default: 21
  user:
    description:
      - The username used to authenticate with.
    required: False
    default: null
  password:
    description:
      - The password used to authenticate with.
    required: False
    default: null
  src:
    description:
      - Path on the source host that will be synchronized to the destination.
    type: path
    required: true
  dest:
    description:
      - Path on the destination host that will be synchronized from the source.
    type: path
    required: true
  protocol:
    description:
      - FTP protocol to use.
    type: string
    required: False
    choices:
      - ftp
      - ftps
    default: ftp
  direction:
    description:
      - Specify the direction of the synchronization. In push mode the localhost or delegate is the source; In pull mode the remote FTP server is the source.
    type: string
    required: False
    choices:
      - push
      - pull
    default: push
  ftp_mode:
    description:
      - FTP mode.
    type: string
    required: False
    choices:
      - passive
      - active
    default: passive
  timeout:
    description:
      - Timeout in seconds for FTP request.
    type: int
    required: False
  backup:
    description:
      - Create a remote backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.
    type: bool
    required: False
    default: False
  retries:
    description:
      - Specifies the number of retries the upload should by tried before it is considered failed.
    type: int
    required: False
    default: 3
  interval:
    description:
      - Configures the interval in seconds to wait between retries of the upload.
    type: int
    required: False
    default: 1
  tmp_dest:
    description:
      - Absolute path of where temporary file is downloaded to.
      - Defaults to C(TMPDIR), C(TEMP) or C(TMP) env variables or a platform specific value.
      - U(https://docs.python.org/2/library/tempfile.html#tempfile.tempdir).
    type: string
    required: False
  others:
    description:
      - All arguments accepted by the file module also work when direction is pull.
    required: False
"""

EXAMPLES = """
# Upload a local file to a remote FTP server
- local_action:
    module: ftp
    host: my.ftp.server.net
    user: myuser
    password: mypassword
    src: /tmp/myfile.txt
    dest: /dest
    direction: push

# Download a directory from a remote FTP server
- local_action:
    module: ftp
    host: my.ftp.server.net
    user: myuser
    password: mypassword
    src: /backups
    dest: /var/backups/
    direction: pull
"""


def _ftp_retry(function):
    """Decorator to retry FTP commands in the case of a connection failure."""

    def wrapper(module, *args, **kwargs):
        retries = module.params["retries"]
        interval = module.params["interval"]

        for _ in range(retries):
            try:
                return function(module, *args, **kwargs)
            except ftplib.all_errors:
                time.sleep(interval)
        return function(module, *args, **kwargs)

    return wrapper


class _FTPPathStatus(Enum):
    """Enumeration for FTP path types."""

    IS_DIR = 1
    IS_FILE = 2
    NOT_EXISTS = 3


@_ftp_retry
def _ftp_check_path(module, session, path):
    """Check whether a remote path on the FTP server is a file, a directory or
    doesn't exist."""

    try:
        content = session.nlst(path)
        # Filter out current and parent directory
        content = [p for p in content if not p.endswith(("/.", "/.."))]
        if len(content) != 1:
            return (_FTPPathStatus.IS_DIR, content)
        if content[0] == path:
            return (_FTPPathStatus.IS_FILE, None)
        return (_FTPPathStatus.IS_DIR, content)
    except ftplib.all_errors as ex:
        code = ex.args[0][:3]
        if code not in ("450", "550"):
            raise ex
        return (_FTPPathStatus.NOT_EXISTS, None)


@_ftp_retry
def _ftp_compare_files(module, session, local_path, remote_path):
    """Check whether a local file and a remote one on a FTP server are
    identical."""

    # Get local file MD5 hash
    local_path_hash = module.md5(local_path)

    # Get remote file MD5 hash
    md5 = hashlib.md5()
    session.retrbinary("RETR {}".format(remote_path), md5.update)
    remote_path_hash = md5.hexdigest()

    return local_path_hash == remote_path_hash


@_ftp_retry
def _ftp_mkdir(module, session, path):
    """Create directory (and its parents) on remote FTP server."""

    sub_dirs = path.split("/")
    current_dir = ""
    for dir_ in sub_dirs:
        if not dir_:
            continue
        current_dir += "/{}".format(dir_)
        try:
            session.mkd(current_dir)
        except ftplib.error_perm as ex:
            code = ex.args[0][:3]
            # Directory already exists
            if code != "550":
                raise ex


@_ftp_retry
def _ftp_backup_file(module, session, path):
    """Create a remote backup file."""

    # Note: don't use colons in backup suffix filename (MS doesn't support it)
    ext = time.strftime("%Y-%m-%d@%H.%M.%S~", time.localtime(time.time()))
    backup_path = "{}.{}.{}".format(path, os.getpid(), ext)
    session.rename(path, backup_path)

    return backup_path


@_ftp_retry
def _ftp_upload_file(module, session, src, dest):
    """Upload a local file to a FTP server."""

    # Upload file
    with open(src, "rb") as src_object:
        session.storbinary("STOR {}".format(dest), src_object)


@_ftp_retry
def _ftp_download_file(module, session, src, dest):
    """Download a remote file from a FTP server."""

    # Upload file
    with open(dest, "wb") as dest_object:
        session.retrbinary("RETR {}".format(src), dest_object.write)


def _ftp_upload(module, session, src, dest, top_dir=True):
    """Upload a local file or directory to a FTP server."""

    dest_is_dir = dest.strip().endswith("/")
    src = os.path.normpath(src)
    dest = os.path.normpath(dest)

    results = {}
    results["src"] = src
    results["dest"] = dest

    if not os.path.exists(src):
        module.fail_json(msg="Source {} does not exist".format(src))
    if not os.access(src, os.R_OK):
        module.fail_json(msg="Source {} is not readable".format(src))
    if not os.path.isfile(src) and not os.path.isdir(src):
        module.fail_json(
            msg="Source {} is not a regular file or a directory".format(src)
        )

    try:
        dest_status, _ = _ftp_check_path(module, session, dest)
    except ftplib.all_errors as ex:
        module.fail_json(
            msg="Unable to get status for destination {}: {}".format(
                dest, to_native(ex)
            )
        )

    dest_exists = dest_status != _FTPPathStatus.NOT_EXISTS
    results["changed"] = not dest_exists
    dest_is_dir |= dest_status == _FTPPathStatus.IS_DIR or os.path.isdir(src)

    if os.path.isdir(src) and dest_status == _FTPPathStatus.IS_FILE:
        module.fail_json(
            msg="Destination {} is a file whereas source {} is a "
            "directory".format(dest, src)
        )

    # Create remote parent directories
    if not dest_exists:
        dest_dir = dest if dest_is_dir else "/".join(dest.split("/")[:-1])

        try:
            _ftp_mkdir(module, session, dest_dir)
        except ftplib.all_errors as ex:
            module.fail_json(
                msg="Unable to create destination directory {}: {}".format(
                    dest, to_native(ex)
                )
            )

    # Manage recursive upload
    if os.path.isdir(src):
        if dest_exists and top_dir:
            dest += "/{}".format(os.path.basename(src))

        for path in os.listdir(src):
            path_src = os.path.join(src, path)
            path_dest = path_src.replace(src, dest, 1).replace(
                os.path.sep, "/"
            )
            path_results = _ftp_upload(
                module, session, path_src, path_dest, False
            )
            results["changed"] |= path_results["changed"]
        return results

    if dest_is_dir:
        dest += "/{}".format(os.path.basename(src))
        # Get status for destination file
        try:
            dest_status, _ = _ftp_check_path(module, session, dest)
        except ftplib.all_errors as ex:
            module.fail_json(
                msg="Unable to get status for destination {}: {}".format(
                    dest, to_native(ex)
                )
            )
        dest_exists = dest_status != _FTPPathStatus.NOT_EXISTS

    results["changed"] |= not dest_exists or not _ftp_compare_files(
        module, session, src, dest
    )

    if results["changed"]:
        try:
            if module.params["backup"] and dest_exists:
                results["backup_file"] = _ftp_backup_file(
                    module, session, dest
                )
        except ftplib.all_errors as ex:
            module.fail_json(
                msg="Unable to backup destination {}: {}".format(
                    dest, to_native(ex)
                )
            )

        try:
            _ftp_upload_file(module, session, src, dest)
        except ftplib.all_errors as ex:
            module.fail_json(
                msg="Unable to upload source {} to destination {}: {}".format(
                    src, dest, to_native(ex)
                )
            )

    return results


def _ftp_download(module, session, src, dest, top_dir=True):
    """Download a remote file or directory from a FTP server."""

    dest_is_dir = dest.endswith("/")

    src = os.path.normpath(src)
    dest = os.path.normpath(dest)

    results = {}
    results["src"] = src
    results["dest"] = dest

    dest_exists = os.path.exists(dest)

    try:
        src_status, src_content = _ftp_check_path(module, session, src)
    except ftplib.all_errors as ex:
        module.fail_json(
            msg="Unable to get status for source {}: {}".format(
                src, to_native(ex)
            )
        )

    if src_status == _FTPPathStatus.NOT_EXISTS:
        module.fail_json(msg="Source {} does not exist".format(src))

    dest_is_dir |= src_status == _FTPPathStatus.IS_DIR or os.path.isdir(dest)
    if dest_exists:
        if not os.access(dest, os.W_OK):
            module.fail_json(msg="Destination {} is not writable".format(dest))
        if not dest_is_dir and not os.path.isfile(dest):
            module.fail_json(
                msg="Destination {} is not a regular file or a "
                "directory".format(dest)
            )

    if dest_exists and not dest_is_dir and src_status == _FTPPathStatus.IS_DIR:
        module.fail_json(
            msg="Source {} is a directory whereas destination {} is not a "
            "directory".format(dest, src)
        )

    results["changed"] = not dest_exists

    # Create local parent directories
    if not dest_exists:
        dest_dir = dest if dest_is_dir else os.path.dirname(dest)
        makedirs_safe(dest_dir, mode=module.params["directory_mode"])

    # Manage recursive download
    if src_status == _FTPPathStatus.IS_DIR:
        if dest_exists and top_dir:
            dest = os.path.join(dest, src.split("/")[-1])

        for path in src_content:
            path_dest = path.replace(src, dest, 1).replace("/", os.path.sep)
            path_results = _ftp_download(
                module, session, path, path_dest, False
            )
            results["changed"] |= path_results["changed"]
        return results

    if dest_is_dir:
        dest = os.path.join(dest, os.path.basename(src))
        dest_exists = os.path.exists(dest)

    results["changed"] |= not dest_exists or not _ftp_compare_files(
        module, session, dest, src
    )

    if results["changed"]:
        tmp_dest = module.params.get("tmp_dest")
        if tmp_dest:
            # tmp_dest should be an existing dir
            if not os.path.isdir(tmp_dest):
                if os.path.exists(tmp_dest):
                    module.fail_json(
                        msg="{} is a file but should be a directory".format(
                            tmp_dest
                        )
                    )
                else:
                    module.fail_json(
                        msg="{} directory does not exist".format(tmp_dest)
                    )

            _, tmp_dest_path = tempfile.mkstemp(dir=tmp_dest)
        else:
            _, tmp_dest_path = tempfile.mkstemp()

        try:
            _ftp_download_file(module, session, src, tmp_dest_path)
        except ftplib.all_errors as ex:
            module.fail_json(
                msg="Unable to download source {} to destination {}: "
                "{}".format(src, dest, to_native(ex))
            )

        if module.params["backup"] and dest_exists:
            results["backup_file"] = module.backup_local(dest)

        module.atomic_move(
            tmp_dest_path, dest, unsafe_writes=module.params["unsafe_writes"]
        )
        file_args = module.load_file_common_arguments(module.params)
        results["changed"] = module.set_file_attributes_if_different(
            file_args, results["changed"]
        )

    return results


@_ftp_retry
def _ftp_connect(module, session):
    session.connect(
        module.params["host"], module.params["port"], module.params["timeout"]
    )
    session.set_pasv(module.params["ftp_mode"] == "passive")
    session.login(module.params["user"], module.params["password"])
    if module.params["protocol"] == "ftps":
        session.prot_p()


def main():
    """Main execution path."""

    module = AnsibleModule(
        argument_spec={
            "host": {"type": "str", "required": True},
            "port": {"type": "int", "default": 21},
            "user": {"type": "str"},
            "password": {"type": "str", "no_log": True},
            "src": {"type": "path", "required": True},
            "dest": {"type": "path", "required": True},
            "direction": {
                "type": "str",
                "choices": ["push", "pull"],
                "default": "push",
            },
            "protocol": {
                "type": "str",
                "choices": ["ftp", "ftps"],
                "default": "ftp",
            },
            "ftp_mode": {
                "type": "str",
                "choices": ["passive", "active"],
                "default": "passive",
            },
            "timeout": {"type": "int"},
            "retries": {"type": "int", "default": 3},
            "interval": {"type": "int", "default": 1},
            "tmp_dest": {"type": "path"},
        },
        add_file_common_args=True,
    )

    protocol = module.params["protocol"]
    if protocol == "ftp":
        from ftplib import FTP
    elif protocol == "ftps":
        from ftplib import FTP_TLS as FTP

    with contextlib.closing(FTP()) as session:
        try:
            _ftp_connect(module, session)
        except ftplib.all_errors as ex:
            module.fail_json(
                msg="Unable to connect to FTP server: {}".format(to_native(ex))
            )

        results = None
        direction = module.params["direction"]
        if direction == "push":
            results = _ftp_upload(
                module, session, module.params["src"], module.params["dest"]
            )
        elif direction == "pull":
            results = _ftp_download(
                module, session, module.params["src"], module.params["dest"]
            )
        module.exit_json(**results)


if __name__ == "__main__":
    main()
