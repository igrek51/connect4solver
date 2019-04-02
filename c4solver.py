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

    def to2d(self):
        return [
            [self.get(x, y) for y in range(BOARD_H)]
            for x in range(BOARD_W)
        ]

    def put(self, x: int, value: str):
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


class WinChecker(object):
    @staticmethod
    def won(grid: Grid) -> Optional[str]:
        return None



def main():
    ap = glue.ArgsProcessor(app_name='Connect 4 solver', version='1.0.0')
    ap.add_param('player', help='select your player', choices=['A', 'B'])
    ap.process()


if __name__ == '__main__':
    main()
