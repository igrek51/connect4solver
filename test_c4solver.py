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
    array = Grid.parse('''
.......
.......
......B
......B
.B....A
.A.A..B
'''.strip()).to2d()
    assert array[1][0] is DISC_A
    assert array[1][1] is DISC_B
    assert array[0][0] is None


# --- Test Grid Validator

