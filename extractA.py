#!/usr/bin/env python3

import os
from pathlib import Path


def extractA(filename):
    with open(filename, "rb") as file:
        tables_count = int.from_bytes(file.read(4), byteorder='little')
        _ = int.from_bytes(file.read(4), byteorder='little')
        table_offset = [0] * tables_count
        for n in range(tables_count):
            offset = int.from_bytes(file.read(4), byteorder='little')
            table_offset[n] = offset
        basename = filename.name
        directory = Path(filename.stem)
        directory.mkdir(exist_ok=True)
        with open(directory / "filelist.txt", "w") as filelist:
            file_length = os.fstat(file.fileno()).st_size
            print(f"{basename} {file_length}", file=filelist)
            for n in range(tables_count):
                if table_offset[n] == 0xffffffff:
                    print(f"Can't create {directory}/string_table_{n}.txt "
                          f"(null table), skipping.")
                    print(f"string_table_{n}.txt", file=filelist)
                    continue
                file.seek(table_offset[n])
                print(f"Creating {directory}/string_table_{n}.txt")
                with open(directory / f"string_table_{n}.txt", "w") as string_table:
                    print(f"string_table_{n}.txt", file=filelist)
                    # skip offset section (not needed?)
                    offset_count = 0
                    while file.read(4) != b'\xff\xff\xff\xff':
                        offset_count += 1
                    if offset_count != 0:
                        for bytestring in read_table(file)[:-1]:
                            string = bytestring.decode()
                            string = string.replace('\n', '<NEWLINE>')
                            if string == "":
                                string_table.write("<EMPTY STRING>")
                            else:
                                string_table.write(string)
                            string_table.write('\n')
            padding_data = file.read()
            print(f"Creating {directory}/enddata.bin")
            with open(directory / "enddata.bin", "wb") as end:
                end.write(padding_data)
            print("enddata.bin", file=filelist)
    print("Finished!")


def read_table(file):
    last_byte = None
    table = bytearray()
    while True:
        cur_byte = file.read(1)
        assert cur_byte != b'', "should not have reached EOF"
        if cur_byte == b'\x00' and last_byte == b'\x00':
            break
        last_byte = cur_byte
        table += cur_byte
    return table.split(b'\x00')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="mhtools.py",
    )
    parser.add_argument('bin_file')

    args = parser.parse_args()

    input_bin = Path(args.bin_file)
    extractA(input_bin)
