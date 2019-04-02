# -*- coding: utf-8 -*-
import mock

from c4solver import *
import sys

from io import StringIO


class MockOutput:
    def __init__(self):
        self.new_out, self.new_err = StringIO(), StringIO()
        self.old_out, self.old_err = sys.stdout, sys.stderr

    def __enter__(self):
        sys.stdout, sys.stderr = self.new_out, self.new_err
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout, sys.stderr = self.old_out, self.old_err

    def output(self):
        return self.new_out.getvalue().strip()

    def assert_contains(self, in_str):
        assert in_str.strip() in self.output()


def test_pytest():
    assert True

# --- Test Grid

def test_print_empty_grid():
    with MockOutput() as mocko:
        Grid().print()
        expected = '''
+---------------+
| . . . . . . . |
| . . . . . . . |
| . . . . . . . |
| . . . . . . . |
| . . . . . . . |
| . . . . . . . |
+---------------+
| 0 1 2 3 4 5 6 |
'''
        mocko.assert_contains(expected.strip())

def test_print_grid_with_disks_put():
    grid = Grid().put(1, DISC_A).put(1, DISC_B).put(3, DISC_A)
    with MockOutput() as mocko:
        grid.print()
        expected = '''
+---------------+
| . . . . . . . |
| . . . . . . . |
| . . . . . . . |
| . . . . . . . |
| . B . . . . . |
| . A . A . . . |
+---------------+
'''
        mocko.assert_contains(expected.strip())
    assert grid.get(1, 0) == DISC_A
    assert grid.get(1, 1) == DISC_B
    assert grid.get(0, 0) is None
    
def test_parse_grid():
    grid = Grid.parse('''
.......
.......
......B
......B
.B....A
.A.A..B
'''.strip())
    with MockOutput() as mocko:
        grid.print()
        mocko.assert_contains('''
+---------------+
| . . . . . . . |
| . . . . . . . |
| . . . . . . B |
| . . . . . . B |
| . B . . . . A |
| . A . A . . B |
+---------------+
'''.strip())

def test_grid_to2d():
    grid = Grid.parse('''
.......
.......
......B
......B
.B....A
.A.A..B
'''.strip())
    array = grid.to2d_xy()
    assert array[1][0] is DISC_A
    assert array[1][1] is DISC_B
    assert array[0][0] is None

    array = grid.to2d_yx()
    assert array[0][1] is DISC_A
    assert array[1][1] is DISC_B
    assert array[0][0] is None

def test_grid_clone():
    grid1 = Grid.parse('''
.......
.......
......B
......B
.B....A
.A.A..B
'''.strip())
    grid2 = grid1.clone()
    grid1.set(1, 0, DISC_B)

    assert grid1.get(1, 0) is DISC_B
    assert grid2.get(1, 0) is DISC_A
    assert grid2.get(1, 2) is None


# --- Test Win Checker

def test_win_checker_none():
    assert Grid().winner() is None
    assert Grid.parse('''
.......
.......
......B
.A....B
.B.BA.A
.A.AB.B
'''.strip()).winner() is None
    
def test_win_checker_vertical():
    assert Grid.parse('''
.......
.......
......A
......A
.B....A
.A.A..A
'''.strip()).winner() is DISC_A
    
def test_win_checker_horizontal():
    assert Grid.parse('''
.......
.......
......A
......A
.B.BBBB
AA.ABBA
'''.strip()).winner() is DISC_B
    
def test_win_checker_diagonal():
    assert Grid.parse('''
.......
.......
......A
.....AA
.B.BABB
AA.ABBA
'''.strip()).winner() is DISC_A
    assert Grid.parse('''
.......
.......
.B....B
.AB..AA
.BABABB
ABAABBA
'''.strip()).winner() is DISC_B
    assert Grid.parse('''
...B...
..BB...
.BBB..B
BAAA.AA
AAAB.B.
AABA.BA
'''.strip()).winner() is DISC_B

def list_winner(l):
    try:
        WinChecker._check_list(l)
    except WinCondition as e:
        return e.winner

def test_win_checker_streak_check():
    assert list_winner([]) is None
    assert list_winner([DISC_A]) is None
    assert list_winner([DISC_A, DISC_A, DISC_A, DISC_A]) is DISC_A
    assert list_winner([DISC_A, DISC_A, DISC_A, DISC_A, None, None]) is DISC_A
    assert list_winner([None, None, DISC_A, DISC_A, DISC_A, DISC_A]) is DISC_A
    assert list_winner([DISC_A, DISC_B, DISC_B, DISC_B, DISC_B]) is DISC_B
    assert list_winner([None, DISC_A, DISC_A, None, DISC_B, DISC_B, DISC_B, DISC_B, None]) is DISC_B












