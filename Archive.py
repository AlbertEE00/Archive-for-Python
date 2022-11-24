#!/usr/bin/python -u
#
# Archive library
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#

import argparse
import os
import pathlib


def get_file_name(filepath: str | os.path(), ext: bool) -> str:
    """Returns the name of the file with or without extension.

    Args:
        filepath (str | os.path): full path to file or relative to script.
        ext (bool): whether to return with extension.

    Returns:
        str: name of the file with or without extension.
    """
    # if extension true return with extension
    if ext:
        return os.path.basename((os.path.abspath(filepath)))
    # return without extension
    return os.path.splitext(os.path.basename((os.path.abspath(filepath))))[0]


def get_file_extension(filepath: str | os.path()) -> str:
    """_summary_

    Args:
        filepath (str | os.path): _description_

    Returns:
        str: _description_
    """
    return pathlib.Path((os.path.abspath(filepath))).suffix


def get_file_directory(filepath: str | os.path()) -> os.path():
    return os.path.dirname((os.path.abspath(filepath)))


class ArchiveFile:
    full_file_path = os.path()
    filename = str()
    file_extension = str()
    directory_path = os.path()

    def __init__(self, file_path):
        self.full_file_path = os.path.abspath(file_path)  # get full file path


def setup_parser():
    # help flag provides flag help
    # store_true actions stores argument as True

    parser = argparse.ArgumentParser("Azoteq testing file sorter")
    subparser = parser.add_subparsers(dest='command')

    extract = subparser.add_parser('extract')
    extract.add_argument('filepath', help="Full path to file", type=str)
    extract.add_argument('-cd', '--currentdir', action='store_true',
                         help="extract to current directory in a folder with file name")
    extract.add_argument('-fn', '--foldername', type=str,
                         help="extract to current directory in a folder with given folder name")
    extract.add_argument('-p', '--path', type=str, help="extract to path entered")
    extract.add_argument('-am', '--automove', action='store_true', help="automatically move to root dir")
    extract.add_argument('-da', '--deletearchive', action='store_true',
                         help="automatically delete archive after extract")
    extract.add_argument('-t', '--type', action='append', help="extract only types specified")
    extract.add_argument('-f', '--files', type=str, nargs="+", help="extract only files specified")

    # parser.add_argument('filepath', help="Full path to file",type=str)
    parser.add_argument('-v', '--view', action='store_true', help="shows contents")
    parser.add_argument('-m', '--move', type=str, help="move file to specified location")
    return parser.parse_args()


if __name__ == "__main__":
    setup_parser()
