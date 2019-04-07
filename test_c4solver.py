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
    grid = Grid().put(1, PA).put(1, PB).put(3, PA)
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
    assert grid.get(1, 0) == PA
    assert grid.get(1, 1) == PB
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

def test_smaller_grid():
    grid = Grid.parse('''
...
.AB
'''.strip())
    with MockOutput() as mocko:
        grid.print()
        mocko.assert_contains('''
+-------+
| . . . |
| . A B |
+-------+
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
    assert array[1][0] == PA
    assert array[1][1] == PB
    assert array[0][0] is None

    array = grid.to2d_yx()
    assert array[0][1] == PA
    assert array[1][1] == PB
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
    grid1.set(1, 0, PB)

    assert grid1.get(1, 0) == PB
    assert grid2.get(1, 0) == PA
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
'''.strip()).winner() == PA
    
def test_win_checker_horizontal():
    assert Grid.parse('''
.......
.......
......A
......A
.B.BBBB
AA.ABBA
'''.strip()).winner() == PB
    
def test_win_checker_diagonal():
    assert Grid.parse('''
.......
.......
......A
.....AA
.B.BABB
AA.ABBA
'''.strip()).winner() == PA
    assert Grid.parse('''
.......
.......
.B....B
.AB..AA
.BABABB
ABAABBA
'''.strip()).winner() == PB
    assert Grid.parse('''
...B...
..BB...
.BBB..B
BAAA.AA
AAAB.B.
AABA.BA
'''.strip()).winner() == PB

def list_winner(l):
    try:
        WinChecker._check_list(l, 4)
    except WinCondition as e:
        return e.winner

def test_win_checker_streak_check():
    assert list_winner([]) is None
    assert list_winner([PA]) is None
    assert list_winner([PA, PA, PA, PA]) == PA
    assert list_winner([PA, PA, PA, PA, None, None]) == PA
    assert list_winner([None, None, PA, PA, PA, PA]) == PA
    assert list_winner([PA, PB, PB, PB, PB]) == PB
    assert list_winner([None, PA, PA, None, PB, PB, PB, PB, None]) == PB

def test_min_win_condition():
    assert Grid.parse('''
...
.A.
AAB
'''.strip(), min_win=2).winner() == PA
    assert Grid.parse('''
...
..A
ABB
'''.strip(), min_win=2).winner() == PB

# --- Move Best Results

def test_best_result_simplest4():
    grid = Grid.parse('''
....
ABAB
ABAB
ABAB
'''.strip())
    searcher = DepthFirstSearcher(PA)
    assert searcher.best_result_on_move(grid, PA, 0) == WIN
    assert searcher.best_result_on_move(grid, PA, 0) == WIN
    assert searcher.best_result_on_move(grid, PA, 1) == LOSE
    assert searcher.best_result_on_move(grid, PA, 2) == WIN
    assert searcher.best_result_on_move(grid, PA, 3) == LOSE
    assert searcher.best_result(grid, PA) == WIN

def test_best_result_simple_tie():
    grid = Grid.parse('''
..
AB
AB
AB
'''.strip())
    searcher = DepthFirstSearcher(PA)
    assert searcher.best_result_on_move(grid, PA, 0) == WIN
    assert searcher.best_result_on_move(grid, PA, 1) == TIE
    assert searcher.best_result(grid, PA) == WIN

def test_best_result_none():
    grid = Grid.parse('''
BA
AB
AB
AB
'''.strip())
    searcher = DepthFirstSearcher(PA)
    assert searcher.best_result_on_move(grid, PA, 0) is None
    grid = Grid.parse('''
BA
AB
AB
AB
'''.strip())
    searcher = DepthFirstSearcher(PA)
    assert searcher.best_result(grid, PA) is TIE


def test_best_result_3x3_tie():
    grid = Grid.parse('''
...
...
...
'''.strip())
    assert moves_results(grid, PA, PA) == [TIE, TIE, TIE]


def test_best_result_3x3_tic_tac_toe():
    grid = Grid(w=3, h=3, min_win=3)
    assert moves_results(grid, PA, PA) == [TIE, TIE, TIE]


def test_best_result_unfair_3x3_tic_tac_toe():
    grid = Grid(w=3, h=3, min_win=2)
    searcher = DepthFirstSearcher(PA)
    assert searcher.best_result_on_move(grid, PA, 1) == WIN
    assert moves_results(grid, PA, PA) == [WIN, WIN, WIN]
    grid = Grid(w=3, h=3, min_win=2)
    assert moves_results(grid, my_player=PA, moving_player=PB) == [LOSE, LOSE, LOSE]




