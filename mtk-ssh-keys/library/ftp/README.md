# ftp

Transfers files and directories from or to ftp servers.

## Synopsis

Transfers files and directories from or to FTP servers

## Options

| parameter | required | default | choices                                  | comments                                                                                                                                                                                                      |
|-----------|----------|---------|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| src       | yes      |         |                                          | Path on the source host that will be synchronized to the destination.                                                                                                                                         |
| direction | no       | push    | <ul><li>push</li><li>pull</li></ul>      | Specify the direction of the synchronization. In push mode the localhost or delegate is the source; In pull mode the remote FTP server is the source.                                                         |
| protocol  | no       | ftp     | <ul><li>ftp</li><li>ftps</li></ul>       | FTP protocol to use.                                                                                                                                                                                          |
| retries   | no       | 3       |                                          | Specifies the number of retries the upload should by tried before it is considered failed.                                                                                                                    |
| dest      | yes      |         |                                          | Path on the destination host that will be synchronized from the source.                                                                                                                                       |
| interval  | no       | 1       |                                          | Configures the interval in seconds to wait between retries of the upload.                                                                                                                                     |
| host      | yes      |         |                                          | FTP server.                                                                                                                                                                                                   |
| ftp_mode  | no       | passive | <ul><li>passive</li><li>active</li></ul> | FTP mode.                                                                                                                                                                                                     |
| user      | no       |         |                                          | The username used to authenticate with.                                                                                                                                                                       |
| timeout   | no       |         |                                          | Timeout in seconds for FTP request.                                                                                                                                                                           |
| password  | no       |         |                                          | The password used to authenticate with.                                                                                                                                                                       |
| backup    | no       | False   |                                          | Create a remote backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.                                                                |
| port      | no       | 21      |                                          | FTP port.                                                                                                                                                                                                     |
| tmp_dest  | no       |         |                                          | Absolute path of where temporary file is downloaded to.  Defaults to `TMPDIR`, `TEMP` or `TMP` env variables or a platform specific value (https://docs.python.org/2/library/tempfile.html#tempfile.tempdir). |
| others    | no       |         |                                          | All arguments accepted by the file module also work when direction is pull.                                                                                                                                   |

## Examples

```
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
```
