#! /usr/bin/env python3

import argparse
import collections
import ete3
import os
import re
import sys


def compare_trees(nw_fn1, nw_fn2):
    t1=ete3.Tree(nw_fn1)
    t2=ete3.Tree(nw_fn2)

    rf, max_rf, common_leaves, parts_t1, parts_t2 = t1.robinson_foulds(t2)

    print (t1, t2)
    print ("RF distance is %s over a total of %s" %(rf, max_rf))
    print ("Partitions in tree2 that were not found in tree1:", parts_t1 - parts_t2)
    print ("Partitions in tree1 that were not found in tree2:", parts_t2 - parts_t1)


def main():

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'nw_fn1',
        metavar='tree1.nw',
        help='',
    )

    parser.add_argument(
        'nw_fn2',
        metavar='tree2.nw',
        help='',
    )

    args = parser.parse_args()

    compare_trees(args.nw_fn1, args.nw_fn2)


if __name__ == "__main__":
    main()
