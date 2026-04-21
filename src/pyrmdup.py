#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import timeit
import hashlib
import shutil
import argparse
from collections import defaultdict

VERSION = '0.628'
CHUNK_SIZE = 65536


def get_quick_hash(filepath):
    """MD5 of first 1024 bytes — cheap pre-filter."""
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        h.update(f.read(1024))
    return h.hexdigest()


def get_full_hash(filepath):
    """MD5 of entire file."""
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            buf = f.read(CHUNK_SIZE)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def files_equal(f1, f2):
    """Full byte-by-byte comparison."""
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(CHUNK_SIZE)
            b2 = fp2.read(CHUNK_SIZE)
            if b1 != b2:
                return False
            if not b1:
                return True


def group_by_equality(files):
    """Group files by byte-equality. n is small so O(n^2) is fine."""
    groups = []
    ungrouped = list(files)
    while ungrouped:
        ref = ungrouped.pop(0)
        group = [ref]
        remaining = []
        for f in ungrouped:
            if files_equal(ref, f):
                group.append(f)
            else:
                remaining.append(f)
        ungrouped = remaining
        if len(group) >= 2:
            groups.append(group)
    return groups


def find_duplicates(folders, debug=False):
    """Return list of duplicate groups (each group is a list of paths)."""
    size_groups = defaultdict(list)
    errors = []

    for folder in folders:
        if not os.path.exists(folder):
            print(f'Error: {folder} does not exist')
            continue
        for dirpath, _, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(dirpath, filename)
                if debug:
                    print(filepath)
                try:
                    size_groups[os.path.getsize(filepath)].append(filepath)
                except OSError as e:
                    msg = f'Failed to get size of {filepath}: {e}'
                    errors.append(msg)
                    print(msg)

    candidates = {sz: fs for sz, fs in size_groups.items() if len(fs) >= 2}
    print(f'\n* Files with duplicate sizes: {sum(len(v) for v in candidates.values())}')

    duplicates = []

    for size, files in candidates.items():
        quick_groups = defaultdict(list)
        for f in files:
            try:
                quick_groups[get_quick_hash(f)].append(f)
            except OSError as e:
                errors.append(f'Failed to hash {f}: {e}')

        for qfiles in quick_groups.values():
            if len(qfiles) < 2:
                continue

            if size < CHUNK_SIZE:
                # Small files: quick hash covers nearly all content; confirm with byte-compare
                duplicates.extend(group_by_equality(qfiles))
            else:
                # Large files: full MD5 is definitive
                full_groups = defaultdict(list)
                for f in qfiles:
                    try:
                        full_groups[get_full_hash(f)].append(f)
                    except OSError as e:
                        errors.append(f'Failed to hash {f}: {e}')
                duplicates.extend(g for g in full_groups.values() if len(g) >= 2)

    if errors:
        print('\nErrors encountered:')
        for e in errors:
            print(e)

    return duplicates


def unique_dest(dest_dir, filename):
    candidate = os.path.join(dest_dir, filename)
    if not os.path.exists(candidate):
        return candidate
    base, ext = os.path.splitext(filename)
    counter = 1
    while True:
        candidate = os.path.join(dest_dir, f'{base}_{counter}{ext}')
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def write_report(results, move_files):
    dest_dir = 'dupfiles'
    if move_files and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open('result.html', 'w', encoding='utf-8') as out:
        out.write('<html><body>\n')
        for group in results:
            original, dupes = group[0], group[1:]
            out.write(f'[ <a href="{original}">{original}</a> ]<br><ul>\n')
            print(original)
            for f in dupes:
                dest = unique_dest(dest_dir, os.path.basename(f))
                if move_files:
                    shutil.move(f, dest)
                    print(f'  {f} -> {dest}')
                    out.write(f'<li><a href="{dest}">{dest}</a></li>\n')
                else:
                    print(f'  {f}')
                    out.write(f'<li><a href="{f}">{f}</a></li>\n')
            print('-' * 20)
            out.write('</ul>\n')
        out.write(f'<br>Version: {VERSION}<br>\n')
        out.write('</body></html>\n')


def print_help():
    print('\n[Help]')
    print('Usage: pyrmdup [option] FolderName [FolderName ...]')
    print('Options:')
    print('  -d  Print debug log')
    print('  -m  Move duplicate files to dupfiles/ folder')
    print('  -h  Show this help message')
    print('\nThis program DOES NOT GUARANTEE YOUR DATA. Use at your own risk.\n')


def main(args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-m', action='store_true')
    parser.add_argument('-d', action='store_true')
    parser.add_argument('-h', action='store_true')
    parser.add_argument('folders', nargs='*')
    opts = parser.parse_args(args)

    if opts.h or not opts.folders:
        print_help()
        return

    if opts.m:
        print('* Move duplicate files mode')
    if opts.d:
        print('* Debug mode')

    print('* Folders:')
    for f in opts.folders:
        print(f'  {f}')

    print('* Scanning files...')
    results = find_duplicates(opts.folders, debug=opts.d)

    if not results:
        print('\n* No duplicate files found')
        return

    print(f'\n* Found {len(results)} duplicate group(s)')
    write_report(results, opts.m)
    print('\n* Report written to result.html')


if __name__ == '__main__':
    start = timeit.default_timer()
    main(sys.argv[1:])
    print(f'\nVersion {VERSION}  Time: {timeit.default_timer() - start:.3f}s')
