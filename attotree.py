#! /usr/bin/env python3

import argparse
import collections
import os
import re
import sys

from pathlib import Path
from xopen import xopen
from pprint import pprint


def main():

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'txt_fn',
        metavar='input.txt',
        help='',
    )

    parser.add_argument(
        '-p',
        '--param',
        metavar='str',
        dest='param',
        default='',
        help='',
    )

    args = parser.parse_args()


if __name__ == "__main__":
    main()
