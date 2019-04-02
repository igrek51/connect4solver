#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glue

from typing import Optional, List

BOARD_W = 7
BOARD_H = 6

WIN_CONDITION = 4

PA = 'A'
PB = 'B'

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
    def __init__(self, w=BOARD_W, h=BOARD_H):
        self.w = w
        self.h = h
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
        # print('putting {} into {} column'.format(value, x))
        column = self.columns[x]
        if len(column) >= self.h:
            raise RuntimeError('column is already full')
        column.append(value)
        return self

    def can_make_move(self, x: int) -> bool:
        return len(self.columns[x]) < self.h

    @staticmethod
    def parse(txt: str):
        lines = txt.strip().splitlines()[::-1]
        h = len(lines)
        w = len(lines[0])
        grid = Grid(w=w, h=h)
        for line in lines:
            for idx, cell in enumerate(line):
                if cell in {PA, PB}:
                    grid.put(idx, cell)
        return grid

    def winner(self) -> Optional[str]:
        return WinChecker.winner(self)

    def clone(self):
        copy = Grid(w=self.w, h=self.h)
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
            self._check_list(row)

    def _check_vertical(self):
        for column in self.grid.columns:
            self._check_list(column)

    def _diagonal_sublist(self, xstart, ystart, xstep, ystep) -> List[str]:
        sublist = []
        while True:
            sublist.append(self.grid.get(xstart, ystart))
            xstart += xstep
            ystart += ystep
            if xstart < 0 or xstart >= self.grid.w or ystart < 0 or ystart >= self.grid.h:
                return sublist

    def _check_diagonal(self):
        for xstart in range(0, self.grid.w - WIN_CONDITION + 1):
            self._check_list(self._diagonal_sublist(xstart, 0, +1, +1))
        for xstart in range(WIN_CONDITION - 1, self.grid.w):
            self._check_list(self._diagonal_sublist(xstart, 0, -1, +1))
        for ystart in range(1, self.grid.h - WIN_CONDITION + 1):
            self._check_list(self._diagonal_sublist(0, ystart, +1, +1))
            self._check_list(self._diagonal_sublist(self.grid.w - 1, ystart, -1, +1))


    @staticmethod
    def _check_list(l):
        last_disc = None
        streak = 0
        for e in l:
            if last_disc is None or e != last_disc:
                streak = 0
                last_disc = e
            if e:
                streak += 1
            if streak >= WIN_CONDITION:
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

def best_result(grid: Grid, my_player: str, move_player: str, move: int) -> str:
    # make a move
    if not grid.can_make_move(move):
        return None
    grid2 = grid.clone().put(move, move_player)
    winner = grid2.winner()
    if winner:
        if winner == my_player:
            return WIN
        else:
            return LOSE

    # find further possible moves
    next_player = opposite_player(move_player)
    posible_moves_results = []
    for potential_move in range(grid2.w):
        move_result = best_result(grid2, my_player, next_player, potential_move)
        if move_result:
            if my_player == next_player and move_result == WIN:
                return move_result
            if my_player != next_player and move_result == LOSE:
                return move_result
            posible_moves_results.append(move_result)
    
    if not posible_moves_results:
        return TIE

    # if analyzing my_player = next_player moves, best move is max 
    if my_player == next_player:
        return max_possible_move(posible_moves_results)
    else:
        return min_possible_move(posible_moves_results)



def find_best_move_action(ap):
    print('searching for the best move...')
    grid = Grid(3, 3)
    my_player = PA
    move_player = PA
    for move in range(grid.w):
        result = best_result(grid, my_player, move_player, move)
        print('move: {}, result: {}'.format(move, result))


def main():
    ap = glue.ArgsProcessor(app_name='Connect 4 solver', version='1.0.0', default_action=find_best_move_action)
    ap.add_param('player', help='select your player', choices=['A', 'B'])
    ap.process()


if __name__ == '__main__':
    main()
