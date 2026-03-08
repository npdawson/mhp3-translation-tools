#!/usr/bin/env python

import hashlib
import pathlib
import re
import shutil

PS3_OFFSET = 0x6d60000
PSP_OFFSET = 0x6d50000

PS3_HASH = "8328f5774e3106953a9560a0b18c2d49"
PSP_HASH = "8e19a966356a83b8b395957671494bd8"

CHUNK_SIZE = 1024


class Patch:
    def __init__(self, patch_file):
        self.num_files = int.from_bytes(patch_file.read(4), byteorder='little')
        self.offsets = []
        self.lengths = []
        headerlen = self.num_files * 8 + 4
        headerpad = -headerlen % 16
        self.data_offset = headerlen + headerpad

        for n in range(self.num_files):
            offset = int.from_bytes(patch_file.read(4), byteorder='little')
            length = int.from_bytes(patch_file.read(4), byteorder='little')
            self.offsets.append(offset)
            self.lengths.append(length)


def check_iso(iso_path):
    print("checking ISO file checksum...")
    with open(iso_path, "rb") as iso_file:
        iso_hash = hashlib.file_digest(iso_file, "md5").hexdigest()
        if iso_hash == PS3_HASH:
            return "ps3"
        elif iso_hash == PSP_HASH:
            return "psp"
        else:
            return iso_hash


def patch_iso(patch_path, iso_path, version):
    print("patching ISO...")

    if version == "psp":
        iso_offset = PSP_OFFSET
    elif version == "ps3":
        iso_offset = PS3_OFFSET
    else:
        assert False

    with open(iso_path, "r+b") as iso, open(patch_path, "rb") as patch:
        patchinfo = Patch(patch)
        patch.seek(patchinfo.data_offset)
        for n in range(patchinfo.num_files):
            iso.seek(iso_offset + patchinfo.offsets[n])
            numbytes = patchinfo.lengths[n]
            while numbytes >= CHUNK_SIZE:
                chunk = patch.read(CHUNK_SIZE)
                iso.write(chunk)
                numbytes -= CHUNK_SIZE
            assert numbytes == 0
    print("Finished patching!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog='patch-iso.py',
        description='''patches a Portable 3rd ISO with a patch file made by
            mhtools.jar'''
    )
    parser.add_argument('patch_filename')
    parser.add_argument('iso_filename')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    version = check_iso(args.iso_filename)
    match version:
        case "ps3":
            print("Monster Hunter Portable 3rd HD ISO matched")
        case "psp":
            print("Monster Hunter Portable 3rd ISO matched")
        case _:
            print("unrecognized ISO file!")
            exit(1)

    output_iso = args.output
    if output_iso is None:
        input_filename = pathlib.Path(args.iso_filename).name
        output_iso = re.sub(r"\.iso$", ".patched.iso",
                            input_filename, flags=re.IGNORECASE)

    print("Making copy of ISO file to patch...")
    shutil.copy2(args.iso_filename, output_iso)

    patch_iso(args.patch_filename, output_iso, version)
