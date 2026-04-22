import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from pyrmdup import (
    get_quick_hash,
    get_full_hash,
    files_equal,
    group_by_equality,
    find_duplicates,
    unique_dest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_file(directory, name, content: bytes) -> str:
    path = os.path.join(directory, name)
    with open(path, 'wb') as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# get_quick_hash
# ---------------------------------------------------------------------------

class TestGetQuickHash:
    def test_same_content_same_hash(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'hello world')
        b = make_file(tmp_path, 'b.bin', b'hello world')
        assert get_quick_hash(a) == get_quick_hash(b)

    def test_different_content_different_hash(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'hello')
        b = make_file(tmp_path, 'b.bin', b'world')
        assert get_quick_hash(a) != get_quick_hash(b)

    def test_only_first_1024_bytes_matter(self, tmp_path):
        # Two files share identical first 1024 bytes but differ after that
        prefix = b'X' * 1024
        a = make_file(tmp_path, 'a.bin', prefix + b'AAA')
        b = make_file(tmp_path, 'b.bin', prefix + b'BBB')
        assert get_quick_hash(a) == get_quick_hash(b)

    def test_empty_file(self, tmp_path):
        a = make_file(tmp_path, 'empty.bin', b'')
        h = get_quick_hash(a)
        assert isinstance(h, str) and len(h) == 32

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(OSError):
            get_quick_hash(str(tmp_path / 'nonexistent.bin'))


# ---------------------------------------------------------------------------
# get_full_hash
# ---------------------------------------------------------------------------

class TestGetFullHash:
    def test_identical_files(self, tmp_path):
        data = b'abc' * 10000
        a = make_file(tmp_path, 'a.bin', data)
        b = make_file(tmp_path, 'b.bin', data)
        assert get_full_hash(a) == get_full_hash(b)

    def test_files_differing_only_at_end(self, tmp_path):
        base = b'Z' * 200_000
        a = make_file(tmp_path, 'a.bin', base + b'\x00')
        b = make_file(tmp_path, 'b.bin', base + b'\xff')
        assert get_full_hash(a) != get_full_hash(b)

    def test_same_prefix_different_suffix_differ_from_quick(self, tmp_path):
        # quick hash collides, full hash must not
        prefix = b'Q' * 1024
        a = make_file(tmp_path, 'a.bin', prefix + b'\x00' * 10000)
        b = make_file(tmp_path, 'b.bin', prefix + b'\xff' * 10000)
        assert get_quick_hash(a) == get_quick_hash(b)
        assert get_full_hash(a) != get_full_hash(b)

    def test_empty_file(self, tmp_path):
        a = make_file(tmp_path, 'empty.bin', b'')
        h = get_full_hash(a)
        assert isinstance(h, str) and len(h) == 32


# ---------------------------------------------------------------------------
# files_equal
# ---------------------------------------------------------------------------

class TestFilesEqual:
    def test_identical_small(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'hello')
        b = make_file(tmp_path, 'b.bin', b'hello')
        assert files_equal(a, b) is True

    def test_different_small(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'hello')
        b = make_file(tmp_path, 'b.bin', b'world')
        assert files_equal(a, b) is False

    def test_identical_large(self, tmp_path):
        data = b'A' * 300_000
        a = make_file(tmp_path, 'a.bin', data)
        b = make_file(tmp_path, 'b.bin', data)
        assert files_equal(a, b) is True

    def test_different_large_end(self, tmp_path):
        # Same first chunk, differ in last byte
        data = b'B' * 200_000
        a = make_file(tmp_path, 'a.bin', data + b'\x00')
        b = make_file(tmp_path, 'b.bin', data + b'\x01')
        assert files_equal(a, b) is False

    def test_different_sizes(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'abc')
        b = make_file(tmp_path, 'b.bin', b'abcd')
        assert files_equal(a, b) is False

    def test_empty_files(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'')
        b = make_file(tmp_path, 'b.bin', b'')
        assert files_equal(a, b) is True


# ---------------------------------------------------------------------------
# group_by_equality
# ---------------------------------------------------------------------------

class TestGroupByEquality:
    def test_two_identical(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'same')
        b = make_file(tmp_path, 'b.bin', b'same')
        groups = group_by_equality([a, b])
        assert len(groups) == 1
        assert set(groups[0]) == {a, b}

    def test_all_unique(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'aaa')
        b = make_file(tmp_path, 'b.bin', b'bbb')
        c = make_file(tmp_path, 'c.bin', b'ccc')
        assert group_by_equality([a, b, c]) == []

    def test_two_groups(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'group1')
        b = make_file(tmp_path, 'b.bin', b'group1')
        c = make_file(tmp_path, 'c.bin', b'group2')
        d = make_file(tmp_path, 'd.bin', b'group2')
        groups = group_by_equality([a, b, c, d])
        assert len(groups) == 2
        sets = [set(g) for g in groups]
        assert {a, b} in sets
        assert {c, d} in sets

    def test_three_identical(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'triple')
        b = make_file(tmp_path, 'b.bin', b'triple')
        c = make_file(tmp_path, 'c.bin', b'triple')
        groups = group_by_equality([a, b, c])
        assert len(groups) == 1
        assert set(groups[0]) == {a, b, c}

    def test_single_file_no_group(self, tmp_path):
        a = make_file(tmp_path, 'a.bin', b'solo')
        assert group_by_equality([a]) == []


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------

class TestFindDuplicates:
    def test_small_duplicates(self, tmp_path):
        make_file(tmp_path, 'a.txt', b'hello')
        make_file(tmp_path, 'b.txt', b'hello')
        make_file(tmp_path, 'c.txt', b'world')
        groups = find_duplicates([str(tmp_path)])
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_no_duplicates(self, tmp_path):
        make_file(tmp_path, 'a.txt', b'aaa')
        make_file(tmp_path, 'b.txt', b'bbb')
        assert find_duplicates([str(tmp_path)]) == []

    def test_large_file_duplicates(self, tmp_path):
        data = b'X' * 200_000
        make_file(tmp_path, 'a.bin', data)
        make_file(tmp_path, 'b.bin', data)
        groups = find_duplicates([str(tmp_path)])
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_large_files_same_prefix_different_content(self, tmp_path):
        prefix = b'P' * 1024
        make_file(tmp_path, 'a.bin', prefix + b'\x00' * 100_000)
        make_file(tmp_path, 'b.bin', prefix + b'\xff' * 100_000)
        assert find_duplicates([str(tmp_path)]) == []

    def test_multiple_folders(self, tmp_path):
        dir_a = tmp_path / 'a'
        dir_b = tmp_path / 'b'
        dir_a.mkdir()
        dir_b.mkdir()
        make_file(str(dir_a), 'f.txt', b'dup')
        make_file(str(dir_b), 'f.txt', b'dup')
        groups = find_duplicates([str(dir_a), str(dir_b)])
        assert len(groups) == 1

    def test_nonexistent_folder(self, tmp_path, capsys):
        find_duplicates([str(tmp_path / 'missing')])
        assert 'does not exist' in capsys.readouterr().out

    def test_recursive_walk(self, tmp_path):
        sub = tmp_path / 'sub'
        sub.mkdir()
        make_file(str(tmp_path), 'a.txt', b'same')
        make_file(str(sub), 'b.txt', b'same')
        groups = find_duplicates([str(tmp_path)])
        assert len(groups) == 1

    def test_same_size_different_content_no_dup(self, tmp_path):
        make_file(tmp_path, 'a.bin', b'abc')
        make_file(tmp_path, 'b.bin', b'xyz')
        assert find_duplicates([str(tmp_path)]) == []

    def test_three_duplicates_one_unique(self, tmp_path):
        make_file(tmp_path, 'a.txt', b'dup')
        make_file(tmp_path, 'b.txt', b'dup')
        make_file(tmp_path, 'c.txt', b'dup')
        make_file(tmp_path, 'd.txt', b'uni')
        groups = find_duplicates([str(tmp_path)])
        assert len(groups) == 1
        assert len(groups[0]) == 3


# ---------------------------------------------------------------------------
# unique_dest
# ---------------------------------------------------------------------------

class TestUniqueDest:
    def test_no_conflict(self, tmp_path):
        result = unique_dest(str(tmp_path), 'file.txt')
        assert result == str(tmp_path / 'file.txt')

    def test_conflict_adds_counter(self, tmp_path):
        make_file(tmp_path, 'file.txt', b'x')
        result = unique_dest(str(tmp_path), 'file.txt')
        assert result == str(tmp_path / 'file_1.txt')

    def test_multiple_conflicts(self, tmp_path):
        make_file(tmp_path, 'file.txt', b'x')
        make_file(tmp_path, 'file_1.txt', b'x')
        result = unique_dest(str(tmp_path), 'file.txt')
        assert result == str(tmp_path / 'file_2.txt')

    def test_no_extension(self, tmp_path):
        make_file(tmp_path, 'noext', b'x')
        result = unique_dest(str(tmp_path), 'noext')
        assert result == str(tmp_path / 'noext_1')
