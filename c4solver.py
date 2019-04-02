#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glue

BOARD_W = 7
BOARD_H = 6

WIN_CONDITION = 4

class Board(object):
    pass


def main():
    ap = glue.ArgsProcessor(app_name='Connect 4 solver', version='1.0.0')
    ap.add_param('player', help='set custom surname', choices=['A', 'B'])
    ap.process()


if __name__ == '__main__':
    main()
