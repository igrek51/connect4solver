#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glue

from typing import Optional

BOARD_W = 7
BOARD_H = 6

WIN_CONDITION = 4

DISC_A = 'A'
DISC_B = 'B'


class Grid(object):
    def __init__(self):
        self.columns = [[] for i in range(BOARD_W)]

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
        print('+-' + '--' * BOARD_W + '+')
        for y in reversed(range(BOARD_H)):
            row_cells = []
            for x in range(BOARD_W):
                cell = self.get(x, y)
                if not cell:
                    cell = '.'
                row_cells.append(cell)
            print('| ' + ' '.join(row_cells) + ' |')
        print('+-' + '--' * BOARD_W + '+')
        print('| ' + ' '.join([str(i) for i in range(BOARD_W)]) + ' |')

    def to2d_xy(self):
        return [
            [self.get(x, y) for y in range(BOARD_H)]
            for x in range(BOARD_W)
        ]

    def to2d_yx(self):
        return [
            [self.get(x, y) for x in range(BOARD_W)]
            for y in range(BOARD_H)
        ]

    def put(self, x: int, value: Optional[str]):
        # print('putting {} into {} column'.format(value, x))
        column = self.columns[x]
        if len(column) >= BOARD_H:
            raise RuntimeError('column is already full')
        column.append(value)
        return self

    @staticmethod
    def parse(txt: str):
        grid = Grid()
        for line in txt.strip().splitlines()[::-1]:
            for idx, cell in enumerate(line):
                if cell in {DISC_A, DISC_B}:
                    grid.put(idx, cell)
        return grid

    def winner(self) -> Optional[str]:
        return WinChecker.winner(self)

    def clone(self):
        copy = Grid()
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
        except WinCondition as e:
            return e.winner

    def _check_horizontal(self):
        for row in self.yx:
            self._check_list(row)

    def _check_vertical(self):
        for column in self.grid.columns:
            self._check_list(column)

    def _check_diagonal(self):
        return None

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


def main():
    ap = glue.ArgsProcessor(app_name='Connect 4 solver', version='1.0.0')
    ap.add_param('player', help='select your player', choices=['A', 'B'])
    ap.process()


if __name__ == '__main__':
    main()
