# -*- coding: utf-8 -*-
"""PyUBCG
Entry point to module

"""

import sys

from PyUBCG.app import Main


def main():
    if len(sys.argv) < 2:
        print('Wrong argument\nFor usage details type:\n\tpyubcg --help')
        exit(1)

    APP = Main()
    APP.run()


if __name__ == '__main__':
    main()
