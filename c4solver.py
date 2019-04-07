#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glue

import datetime
import time
from typing import Optional, List

BOARD_W = 7
BOARD_H = 6

MIN_WIN_CONDITION = 4

PA = 'A'
PB = 'B'

WIN = 'W'
LOSE = 'L'
TIE = 'T'

move_results_weights = {
    WIN: 1,
    TIE: 0,
    LOSE: -1,
}

class Grid(object):
    def __init__(self, w=BOARD_W, h=BOARD_H, min_win=MIN_WIN_CONDITION):
        self.w = w
        self.h = h
        self.min_win = min_win
        self.columns = [[] for i in range(self.w)]

    def get(self, x: int, y: int):
        """axes oriented top-right: y^.->x"""
        column = self.columns[x]
        if y >= len(column):
            return None
        return column[y]

    def set(self, x: int, y: int, value: Optional[str]):
        column = self.columns[x]
        column[y] = value

    def print(self):
        print('+-' + '--' * self.w + '+')
        for y in reversed(range(self.h)):
            row_cells = []
            for x in range(self.w):
                cell = self.get(x, y)
                if not cell:
                    cell = '.'
                row_cells.append(cell)
            print('| ' + ' '.join(row_cells) + ' |')
        print('+-' + '--' * self.w + '+')
        print('| ' + ' '.join([str(i) for i in range(self.w)]) + ' |')

    def to2d_xy(self):
        return [
            [self.get(x, y) for y in range(self.h)]
            for x in range(self.w)
        ]

    def to2d_yx(self):
        return [
            [self.get(x, y) for x in range(self.w)]
            for y in range(self.h)
        ]

    def put(self, x: int, value: Optional[str]):
        column = self.columns[x]
        if len(column) >= self.h:
            raise RuntimeError('column is already full')
        column.append(value)
        return self

    def can_make_move(self, x: int) -> bool:
        return len(self.columns[x]) < self.h

    @staticmethod
    def parse(txt: str, min_win: Optional[int] = MIN_WIN_CONDITION):
        lines = txt.strip().splitlines()[::-1]
        h = len(lines)
        w = len(lines[0])
        grid = Grid(w=w, h=h, min_win=min_win)
        for line in lines:
            for idx, cell in enumerate(line):
                if cell in {PA, PB}:
                    grid.put(idx, cell)
        return grid

    def winner(self) -> Optional[str]:
        return WinChecker.winner(self)

    def clone(self):
        copy = Grid(w=self.w, h=self.h, min_win=self.min_win)
        copy.columns = [column[:] for column in self.columns]
        return copy


class WinCondition(Exception):
    def __init__(self, winner: str):
        self.winner = winner


class WinChecker(object):
    @staticmethod
    def winner(grid: Grid) -> Optional[str]:
        return WinChecker(grid)._winner()

    def __init__(self, grid: Grid):
        self.grid = grid
        self.yx = grid.to2d_yx()

    def _winner(self) -> Optional[str]:
        try:
            self._check_vertical()
            self._check_horizontal()
            self._check_diagonal()
            self._check_diagonal()
        except WinCondition as e:
            return e.winner

    def _check_horizontal(self):
        for row in self.yx:
            self._check_list(row, self.grid.min_win)

    def _check_vertical(self):
        for column in self.grid.columns:
            self._check_list(column, self.grid.min_win)

    def _diagonal_sublist(self, xstart, ystart, xstep, ystep) -> List[str]:
        sublist = []
        while True:
            sublist.append(self.grid.get(xstart, ystart))
            xstart += xstep
            ystart += ystep
            if xstart < 0 or xstart >= self.grid.w or ystart < 0 or ystart >= self.grid.h:
                return sublist

    def _check_diagonal(self):
        for xstart in range(0, self.grid.w - self.grid.min_win + 1):
            self._check_list(self._diagonal_sublist(xstart, 0, +1, +1), self.grid.min_win)
        for xstart in range(self.grid.min_win - 1, self.grid.w):
            self._check_list(self._diagonal_sublist(xstart, 0, -1, +1), self.grid.min_win)
        for ystart in range(1, self.grid.h - self.grid.min_win + 1):
            self._check_list(self._diagonal_sublist(0, ystart, +1, +1), self.grid.min_win)
            self._check_list(self._diagonal_sublist(self.grid.w - 1, ystart, -1, +1), self.grid.min_win)


    @staticmethod
    def _check_list(l, min_win):
        """checks if there's a winning streak"""
        last_disc = None
        streak = 0
        for e in l:
            if last_disc is None or e != last_disc:
                streak = 0
                last_disc = e
            if e:
                streak += 1
            if streak >= min_win:
                raise WinCondition(e)




def opposite_player(player: str) -> str:
    return PB if player == PA else PA


def max_possible_move(posible_moves_results) -> str:
    maxr = posible_moves_results[0]
    for move_result in posible_moves_results:
        if move_results_weights[move_result] > move_results_weights[maxr]:
            maxr = move_result
    return maxr

def min_possible_move(posible_moves_results) -> str:
    minr = posible_moves_results[0]
    for move_result in posible_moves_results:
        if move_results_weights[move_result] < move_results_weights[minr]:
            minr = move_result
    return minr


class ResultsCache(object):
    def __init__(self):
        self.cache = {}

    @staticmethod
    def hashcode(grid: Grid):
        # FIXME hashcode collissions are risky here
        return hash(str(grid.columns))

    def get(self, grid: Grid) -> str:
        return self.cache.get(self.hashcode(grid))

    def put(self, grid: Grid, result: str):
        if result:
            self.cache[self.hashcode(grid)] = result


iterations = 0


class DepthFirstSearcher(object):
    def __init__(self, my_player: str):
        self.my_player = my_player
        self.results_cache = ResultsCache()


    def best_result_on_move(self, grid: Grid, moving_player: str, move: int) -> str:
        # make a move
        if not grid.can_make_move(move):
            return None
        grid_after = grid.clone().put(move, moving_player)

        cached = self.results_cache.get(grid_after)
        if cached:
            return cached

        next_player = opposite_player(moving_player)

        result = self.best_result(grid_after, next_player)

        if result:
            self.results_cache.put(grid_after, result)
        return result


    def best_result(self, grid: Grid, next_player: str) -> str:
        global iterations
        iterations += 1
        if iterations % 100000 == 0:
            print('iterations: ' + str(iterations))

        winner = grid.winner()
        if winner:
            if winner == self.my_player:
                return WIN
            else:
                return LOSE

        # find further possible moves
        posible_moves_results = []
        for potential_move in range(grid.w):
            move_result = self.best_result_on_move(grid, next_player, potential_move)

            if move_result:
                if self.my_player == next_player and move_result == WIN:
                    return move_result
                if self.my_player != next_player and move_result == LOSE:
                    return move_result

                posible_moves_results.append(move_result)
        
        if not posible_moves_results:
            return TIE

        # if analyzing my_player = next_player moves, best move is max 
        if self.my_player == next_player:
            return max_possible_move(posible_moves_results)
        else: # opponent tries to minimize my winning moves
            return min_possible_move(posible_moves_results)


my_player = PA


class PotentialMove(object):
    def __init__(self, grid: Grid, move_player: str, move: int, parent = None):
        self.grid = grid
        self.move_player = move_player
        self.move = move
        self.parent = parent
        self.children = []
        self.result = None

    def set_result(self, result):
        self.result = result
        for child in self.children:
            # FIXME remove from queue as well
            del child
        self.children = []
        self.recalculate()

    def recalculate(self):
        if self.parent:

            if self.result == WIN and self.move_player == my_player:
                self.parent.set_result(self.result)

            elif self.result == LOSE and self.move_player != my_player:
                self.parent.set_result(self.result)

            else:
                child_results = [child.result for child in self.parent.children if child.result]
                if len(child_results) == len(self.parent.children):
                    # all the results are ready
                    if self.move_player == my_player:
                        self.parent.set_result(max_possible_move(child_results))
                    else: # opponent tries to minimize my winning moves
                        self.parent.set_result(min_possible_move(child_results))


class BreadthFirstSearcher(object):
    def __init__(self, my_player: str):
        self.my_player = my_player
        self.moves_que = []



    def best_result_bfs(self, grid: Grid, move_player: str, starting_move: int) -> str:
        if grid.can_make_move(starting_move):
            self.moves_que.append(PotentialMove(grid, move_player, starting_move))

        while self.moves_que:
            move = self.moves_que.popleft()

            self.analyze_move(move)
            move.recalculate()
            # enque analyzing next level moves

            # check if move is valid or is ending the game

            # if the results are ready - infer the conclusion


    def analyze_move(self, potential_move: PotentialMove):
        grid2 = potential_move.grid.clone().put(potential_move.move, potential_move.move_player)
        winner = grid2.winner()
        if winner:
            if winner == my_player:
                potential_move.result = WIN
            else:
                potential_move.result = LOSE
            return

        # find further possible moves, enque analyzing next level moves
        next_player = opposite_player(potential_move.move_player)
        next_moves = []
        for next_move in range(grid2.w):
            if grid2.can_make_move(next_move):
                next_moves.append(next_move)
                potential_move.children.append()
        
        if not next_moves:
            potential_move.result = TIE
            return


def moves_results(grid, my_player, moving_player) -> List[str]:
    searcher = DepthFirstSearcher(my_player)
    return [searcher.best_result_on_move(grid, moving_player, move) for move in range(grid.w)]


def now() -> float:
    return datetime.datetime.now()


def find_moves_results_action(ap):
    print('searching for the moves results...')
    grid = Grid(4, 4)
    grid.print()
    checkpoint = now()
    for idx, result in enumerate(moves_results(grid, PA, PA)):
        print('move: {}, result: {}'.format(idx, result))
    print('iterations: {}'.format(iterations))
    print('duration: {}s'.format(now() - checkpoint))


def main():
    ap = glue.ArgsProcessor(app_name='Connect 4 solver', version='1.0.0', default_action=find_moves_results_action)
    ap.add_param('player', help='select your player', choices=['A', 'B'])
    ap.process()


if __name__ == '__main__':
    main()
