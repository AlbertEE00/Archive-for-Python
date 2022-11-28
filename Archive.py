#!/usr/bin/python -u
# Archive wrapping library for python to work with archives
# Copyright (C) 2022  Albert van Zyl
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import argparse
import gzip
import os
import pathlib
import re
import shutil
import tempfile
import zipfile
from typing import List

import py7zr
import rarfile


def get_file_name(filepath: str | pathlib.Path, ext: bool = False) -> str:
    """
    Returns the name of the file with or without extension.

    Args:
        filepath: Full path to file or relative to script.
        ext (bool): whether to return with extension.

    Returns:
        str: name of the file with or without extension.
    """
    # if extension true return with extension
    if ext:
        return str(os.path.basename((os.path.abspath(filepath))))
    # return without extension
    return str(os.path.splitext(os.path.basename((os.path.abspath(filepath))))[0])


def get_file_extension(filepath: str | pathlib.Path) -> str:
    """
    Returns the extension of the file.

    Args:
        filepath: Full path to file or relative to script.

    Returns:
        str: extension of file.
    """
    return pathlib.Path((os.path.abspath(filepath))).suffix


def get_file_directory(filepath: str | pathlib.Path) -> pathlib.Path:
    """
    Return the directory of the file

    Args:
        filepath: Full path to file or relative to script.

    Returns:
        os.path(): Path to directory of file.

    """
    if os.path.isfile(os.path.abspath(filepath)):
        return os.path.dirname((os.path.abspath(filepath)))
    elif os.path.isdir(os.path.abspath(filepath)):
        return os.path.abspath(filepath)


def check_if_gz_file(filepath: str | pathlib.Path) -> bool:
    GZIP_MAGIC_NUMBER = "31139"
    f = open(filepath, mode='rb')
    first_two = f.read(2)
    if str(first_two[0]) + str(first_two[1]) == GZIP_MAGIC_NUMBER:
        return True
    else:
        return False


class ArchiveFile:
    full_file_path = pathlib.Path()
    directory_path = pathlib.Path()
    file_name = str()
    full_file_name = str()
    file_extension = str()
    file_list = list()
    __initState = False

    def __init__(self, file_path):
        if os.path.exists(os.path.abspath(file_path)):
            self.full_file_path = pathlib.Path(os.path.abspath(file_path))  # get full file path
            self.directory_path = self.full_file_path.parent.absolute()
            self.file_name = self.full_file_path.with_suffix("").name
            self.full_file_name = self.full_file_path.name
            self.file_extension = self.full_file_path.suffix
            self.__initState = True
        else:
            print("Invalid File Path: exiting...")
            exit()
        self.read_contents()

    def read_contents(self, print_files: bool = False, files: List[str] | None = None,
                      file_types: List[str] | None = None,
                      pattern: List[str] | None = None, exclusive: bool = False):
        if not self.__initState:
            return "Archive not initialized"
        if rarfile.is_rarfile(self.full_file_path):
            with rarfile.RarFile(self.full_file_path) as rar:
                self.file_list = rar.namelist()
        elif zipfile.is_zipfile(self.full_file_path):
            with zipfile.ZipFile(self.full_file_path, "r") as zip_file:
                self.file_list = zip_file.namelist()
            # archive.extractall(path=None, members=None, pwd=None)
        elif py7zr.is_7zfile(self.full_file_path):
            with py7zr.SevenZipFile(self.full_file_path, "r") as SevenZip:
                self.file_list = SevenZip.getnames()
        elif check_if_gz_file(self.full_file_path):
            self.file_list = [self.file_name]

        new_list = list()
        if file_types or pattern or files:
            for file in self.file_list:
                append = False
                if file_types:
                    for f_type in file_types:
                        if f_type in get_file_extension(file):
                            append = True
                if pattern:
                    if exclusive:
                        for search in pattern:
                            res = re.findall(search, file)
                            if res:
                                pass
                            else:
                                append = False
                                break
                    else:
                        for search in pattern:
                            res = re.findall(search, file)
                            if res:
                                append = True
                if files:
                    if exclusive:
                        for file_name in files:
                            res = re.findall(file_name, file)
                            if res:
                                pass
                            else:
                                append = False
                                break
                    else:
                        for file_name in files:
                            res = re.findall(file_name, file)
                            if res:
                                append = True
                if append:
                    new_list.append(file)
            self.file_list = new_list
        if print_files:
            for ffile in self.file_list:
                print(ffile)
        return self.file_list

    def extract(self, extract_path: str = None, files_only: bool = False, continuity_check: str = None,
                files: List[str] | None = None, file_types: List[str] | None = None,
                pattern: List[str] | None = None, exclusive: bool = False):
        if not self.__initState:
            return "Archive not initialized"
        # print(f'this is before: {extract_path}')

        if extract_path is not None:
            if r'\\' in extract_path:
                print(f'Invalid Extract Path: {extract_path}, exiting...')
                exit()
        if extract_path == "":  # extract to directory with file name
            if check_if_gz_file(self.full_file_path):
                extract_path = self.directory_path.joinpath(pathlib.Path(self.file_name).with_suffix(""))
            else:
                extract_path = self.directory_path.joinpath(self.file_name)
        else:
            extract_path = pathlib.Path(
                os.path.abspath(extract_path)) if extract_path else self.directory_path  # make a full path and

        self.read_contents(print_files=False, files=files, file_types=file_types, pattern=pattern, exclusive=exclusive)
        if self.file_list.__len__() == 0:
            print(f'Criteria Mismatch: No files to extract from {self.full_file_path} for criteria:')
            if files:
                print()
                print('Files:')
                for f in files:
                    print(f)
            if file_types:
                print()
                print('File types/extensions:')
                for t in file_types:
                    print(t)
            if pattern:
                print()
                print('Search Pattern:')
                for p in pattern:
                    print(p)
            print()
            print("Exiting...")
            exit()
        if extract_path:
            if continuity_check:
                if continuity_check in str(extract_path):
                    pass
                else:
                    print(
                        f'Continuity Check Fail: {continuity_check} failed for extract path {extract_path}, exiting...')
                    exit()
            exist_one_parent = False
            for parent in extract_path.parents:
                if parent.exists():
                    exist_one_parent = True
                    break
            if exist_one_parent:
                extract_path.mkdir(exist_ok=True, parents=True)
            else:
                print(f'Invalid Extract Path: {extract_path}, exiting...')
        # path object
        # print(f'this is after: {extract_path}')
        # extract to directory with file name in archive directory

        print(f'Extracting {self.full_file_path} to path: {extract_path}')
        extract_path_bkup = extract_path

        if files_only:
            if rarfile.is_rarfile(self.full_file_path):
                for i in range(self.file_list.__len__()):
                    rarfile.RarFile(self.full_file_path).extractall(path=extract_path, members=[str(self.file_list[i])],
                                                                    pwd=None)

                    new_path = os.path.join(extract_path, self.file_list[i])
                    if os.path.isfile(new_path):
                        shutil.move(new_path, os.path.join(str(extract_path_bkup),pathlib.Path(new_path).name))  # move files to top dir
            elif zipfile.is_zipfile(self.full_file_path):
                for i in range(self.file_list.__len__()):
                    zipfile.ZipFile(self.full_file_path, "r").extractall(path=extract_path,
                                                                         members=[str(self.file_list[i])],
                                                                         pwd=None)
                    new_path = os.path.join(extract_path, self.file_list[i])
                    if os.path.isfile(new_path):
                        shutil.move(new_path, os.path.join(str(extract_path_bkup), pathlib.Path(new_path).name))  # move files to top dir
            elif py7zr.is_7zfile(self.full_file_path):
                for i in range(self.file_list.__len__()):
                    py7zr.SevenZipFile(self.full_file_path, "r").extract(path=extract_path,
                                                                         targets=[str(self.file_list[i])])
                    new_path = os.path.join(extract_path, self.file_list[i])
                    print(new_path)

                    if os.path.isfile(new_path):
                        shutil.move(new_path, os.path.join(str(extract_path_bkup), pathlib.Path(new_path).name))  # move files to top dir

            elif check_if_gz_file(self.full_file_path):
                with gzip.open(self.full_file_path, 'rb') as f_in:

                    with open(os.path.join(str(extract_path), self.file_name), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            self.read_contents()
            for f in self.file_list:
                new_path = os.path.join(extract_path, f)
                if os.path.isdir(new_path):
                    shutil.rmtree(new_path)
            return extract_path_bkup

        if rarfile.is_rarfile(self.full_file_path):
            with rarfile.RarFile(self.full_file_path) as rar:
                rar.extractall(path=extract_path, members=self.file_list, pwd=None)
        elif zipfile.is_zipfile(self.full_file_path):
            with zipfile.ZipFile(self.full_file_path, "r") as zipper:
                zipper.extractall(path=extract_path, members=self.file_list, pwd=None)
        elif py7zr.is_7zfile(self.full_file_path):
            for i in range(self.file_list.__len__()):
                py7zr.SevenZipFile(self.full_file_path, "r").extract(path=extract_path, targets=self.file_list[i])
        elif check_if_gz_file(self.full_file_path):
            with gzip.open(self.full_file_path, 'rb') as f_in:
                with open(os.path.join(str(extract_path), self.file_name), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

        return extract_path_bkup


def setup_parser():
    # help flag provides flag help
    # store_true actions stores argument as True

    parser = argparse.ArgumentParser(prog="Archive.py", description="Archive management utility", epilog=" ")
    subparser = parser.add_subparsers(dest='command')
    parser.add_argument('archive_path', help="Full path to file", type=str)

    extract = subparser.add_parser('extract', help="extract file to specified location, if no arguments are given "
                                                   "extract all files in archive to directory with name of file in "
                                                   "the directory of the archive")
    extract_group_exclusive = extract.add_mutually_exclusive_group()

    extract_group_exclusive.add_argument('-d', '--destination', type=str,
                                         help="move file to specified location, if only a name is "
                                              "given then to a folder relative to archive location")
    extract_group_exclusive.add_argument('-cd', '--current_dir', action='store_true',
                                         help="extract to current directory")

    extract.add_argument('-cc', '--continuity_check', type=str, help="move all files to a directory")
    extract.add_argument('-fo', '--only_files', action='store_true', help="automatically files only to "
                                                                          "extract directory")
    extract.add_argument('-del', '--delete_archive', action='store_true',
                         help="automatically delete archive after extraction")

    extract.add_argument('-x', '--exclusive', action='store_true', help="extract with exclusive settings")
    extract.add_argument('-t', '--type', action='append', help="extract only types specified, appended with each -t")
    extract.add_argument('-f', '--files', action='append', help="extract only files specified, appended with each -f")
    extract.add_argument('-s', '--search', action='append', help="extract only matches to search specified, appended "
                                                                 "with each "
                                                                 "-s")

    move = subparser.add_parser('move', help="move archive to specified location")
    move.add_argument('destination', type=str, nargs='+', help="move file(s) to specified destination path, if only a "
                                                               "name is "
                                                               "given then to a folder relative to archive location")
    view = subparser.add_parser('view', help="shows contents of archive")
    view.add_argument('-x', '--exclusive', action='store_true', help="view with exclusive settings")
    view.add_argument('-t', '--type', action='append', help="view only types specified, appended with each -t")
    view.add_argument('-f', '--files', action='append', help="view only files specified, appended with each -f")
    view.add_argument('-s', '--search', action='append',
                      help="view only matches to search specified, appended with each "
                           "-s")

    return parser.parse_args()


if __name__ == "__main__":
    args = setup_parser()
    prev_dir = os.getcwd()
    if args.command == "view":
        ArchiveFile(args.archive_path).read_contents(True, args.files, args.type, args.search, args.exclusive)
        os.chdir(ArchiveFile.directory_path)
    elif args.command == "extract":
        archive = ArchiveFile(args.archive_path)
        os.chdir(ArchiveFile.directory_path)
        destination_dir = ""
        if args.current_dir:
            destination_dir = None
        elif args.destination:
            destination_dir = args.destination
        else:
            destination_dir = ""
        temp_des_dir = destination_dir
        final_path = archive.extract(extract_path=destination_dir, files_only=args.only_files, files=args.files,
                                     file_types=args.type, pattern=args.search, exclusive=args.exclusive,
                                     continuity_check=args.continuity_check)

        if args.delete_archive:
            os.remove(args.archive_path)
        os.chdir(prev_dir)
    elif args.command == "move":
        os.chdir(ArchiveFile.directory_path)
        pass
    else:
        print("Invalid command")
        exit()


