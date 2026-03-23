#!/usr/bin/env python3

import gspread
from pathlib import Path
from collections import defaultdict

gc = gspread.oauth()
sh = gc.open("MHP3rd Translation Project")

PSP_WORKSHEET_ID = 1874244777
PS3_WORKSHEET_ID = 1307758665
FILE_REF_ID = 1858240434

# psp_worksheet = sh.get_worksheet_by_id(PSP_WORKSHEET)
ps3_worksheet = sh.get_worksheet_by_id(PS3_WORKSHEET_ID)
# file_ref = sh.get_worksheet_by_id(FILE_REF_ID).get_all_records()

# psp_records = psp_worksheet.get_all_records(numericise_ignore=[1, 4, 7, 8])
ps3_records = ps3_worksheet.get_all_records(numericise_ignore=[1, 4, 5, 6])


def records_to_files(records):
    files = defaultdict(list)
    sorted_records = sorted(records,
                            key=lambda x: (x['bin'], x['file'], x['line']))
    for row in sorted_records:
        path = Path('ps3') / row['bin'] / f"string_table_{row['file']}.txt"
        line = row['EN']
        if line == '':
            line = row['rough translation']
        files[path].append(line)
    return dict(files)


def patch_files(filedict, dir='./'):
    path = Path(dir)
    for filepath, new_lines in filedict.items():
        # sanity checks before we make any changes
        fullpath = path / filepath
        assert fullpath.is_file(), f"File not found: {fullpath}"
        with open(fullpath, 'r') as file:
            file_lines = file.readlines()
            assert len(file_lines) == len(new_lines), \
                f"Number of lines doesn't match: {fullpath}"

    for filepath, new_lines in filedict.items():
        fullpath = path / filepath
        with open(fullpath, 'r') as file:
            file_lines = file.readlines()
        for line_num, new_line in enumerate(new_lines):
            if new_line.strip() != '':
                new_line = new_line.replace('\n', ' ')
                file_lines[line_num] = new_line.rstrip() + '\n'
        with open(fullpath, 'w') as file:
            file.writelines(file_lines)


if __name__ == "__main__":
    ps3_files = records_to_files(ps3_records)
    patch_files(ps3_files)
