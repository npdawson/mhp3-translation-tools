#!/usr/bin/env python3

import os
from pathlib import Path


def extractC(filename):
    index_values = []
    table_offsets = []
    with open(filename, 'rb') as file:
        while True:
            index = int.from_bytes(file.read(4), byteorder='little')
            offset = int.from_bytes(file.read(4), byteorder='little')
            if index == 0xffffffff and offset == 0xffffffff:
                break
            index_values.append(index)
            table_offsets.append(offset)
        basename = filename.name
        directory = Path(filename.stem)
        directory.mkdir(exist_ok=True)
        with open(directory / "filelist.txt", "w") as filelist:
            file_length = os.fstat(file.fileno()).st_size
            print(f"{basename} {file_length}", file=filelist)
            string_table_end = 0
            for n, offset in enumerate(table_offsets):
                file.seek(offset)
                print(f"Creating {directory}/string_table_{n}.txt")
                with open(directory / f"string_table_{n}.txt",
                          "w") as stringtable:
                    print(f"{index_values[n]},string_table_{n}.txt",
                          file=filelist)
                    offset_table_start = file.tell()
                    string_table_start = 0
                    first = False
                    while True:
                        typ = int.from_bytes(file.read(4), byteorder='little')
                        offset = int.from_bytes(file.read(4),
                                                byteorder='little')
                        if not first:
                            first = True
                            string_table_start = offset + offset_table_start
                        actual_offset = file.tell()
                        file.seek(offset + offset_table_start)
                        str = read_string(file)
                        string_table_end = file.tell()
                        file.seek(actual_offset)
                        if len(str) == 0:
                            print(f"{typ},<EMPTY STRING>", file=stringtable)
                        else:
                            print(f"{typ},{str.replace('\n', '<NEWLINE>')}",
                                  file=stringtable)
                        if file.tell() >= string_table_start:
                            break
            file.seek(string_table_end)
            table_end = file.read(2)
            assert table_end == b'\x00\x00', f"table end error! {table_end}"
            padding = file.read()
            print(f"Creating {directory}/enddata.bin")
            print("enddata.bin", file=filelist)
            with open(directory / "enddata.bin", "wb") as end:
                end.write(padding)
    print("Finished!")


def read_string(file):
    str = bytearray()
    while True:
        byte = file.read(1)
        assert byte != b'', "should not have reached EOF"
        if byte == b'\x00':
            return str.decode()
        str += byte


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="mhtools.py",
    )
    parser.add_argument('bin_file')

    args = parser.parse_args()

    input_bin = Path(args.bin_file)
    extractC(input_bin)
