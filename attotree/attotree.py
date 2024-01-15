#! /usr/bin/env python3
"""attotree

Author:  Karel Brinda <karel.brinda@inria.fr>

License: MIT
"""

import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile
import time

sys.path.append(os.path.dirname(__file__))
import version

PROGRAM = 'attotree'
VERSION = version.VERSION
DESC = 'rapid estimation of phylogenetic trees using sketching'

DEFAULT_S = 10000
DEFAULT_K = 21
DEFAULT_T = os.cpu_count()
DEFAULT_F = "nj"


def error(*msg, error_code=1):
    print('attotree error:', *msg, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    #close_log()
    sys.exit(error_code)


def message(*msg):
    dt = datetime.datetime.now()
    fdt = dt.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f'[attotree] {fdt} {" ".join(msg)}'
    print(log_line, file=sys.stderr)


def run_safe(command, output_fn=None, output_fo=None, err_msg=None, thr_exc=True, silent=False):
    """Run a shell command safely.

    Args:
        command (list of str): Command to execute.
        output_fn (str): Name of a file for storing the output.
        output_fo (fileobject): Output file object. If both params are None, the standard output is used.
        err_msg (str): Error message if the command fails.
        thr_exc (bool): Through exception if the command fails. error_msg or thr_exc must be set.
        silent (bool): Silent mode (print messages only if the command fails).
    """

    assert output_fn is None or output_fo is None
    assert err_msg is not None or thr_exc
    assert len(command) > 0

    command_safe = []

    for part in command:
        part = str(part)
        if " " in part:
            part = '"{}"'.format(part)
        command_safe.append(part)

    command_str = " ".join(command_safe)

    if not silent:
        message("Shell command:", command_str)

    if output_fn is None:
        if output_fo is None:
            out_fo = sys.stdout
        else:
            out_fo = output_fo
    else:
        out_fo = open(output_fn, "w+")

    if out_fo == sys.stdout:
        p = subprocess.Popen("/bin/bash -e -o pipefail -c '{}'".format(command_str), shell=True)
    else:
        p = subprocess.Popen("/bin/bash -e -o pipefail -c '{}'".format(command_str), shell=True, stdout=out_fo)

    error_code = None
    while error_code is None:
        time.sleep(0.2)
        error_code = p.poll()

    out_fo.flush()

    if output_fn is not None:
        out_fo.close()

    if error_code == 0 or error_code == 141:
        if not silent:
            message("Finished: {}".format(command_str))
    else:
        message("Unfinished, an error occurred (error code {}): {}".format(error_code, command_str))

        if err_msg is not None:
            print('Error: {}'.format(err_msg), file=sys.stderr)

        if thr_exc:
            error("A command failed, see messages above.")

        sys.exit(1)


def mash_triangle(inp_fns, phylip_fn, k, s, t, fof):
    message("Running mash")
    cmd = f"mash triangle -s {s} -k {k} -p {t}".split()
    if fof:
        cmd += ["-l"]
    cmd += inp_fns
    run_safe(cmd, output_fn=phylip_fn)


def quicktree(phylip_fn, newick_fn, algorithm):
    message("Running quicktree")

    cmd = "quicktree -in m".split()
    if algorithm == "upgma":
        cmd += ["-upgma"]
    cmd += [phylip_fn]
    run_safe(cmd, output_fn=newick_fn)


def postprocess_quicktree_nw(nw1, nw_fo):
    message("Postprocessing tree")
    buffer = []
    with open(nw1) as fo:
        for x in fo:
            x = x.strip()
            # for lines containing names, update the name
            if x and not x[0] in ":(":
                p = x.split(":")
                # remove dirname
                basename_components = os.path.basename(p[0]).split(".")
                if len(basename_components) == 1:
                    basename_components.append("")
                # remove suffix
                p[0] = ".".join(basename_components[:-1])
                # compose the original newick line with an updated name
                x = ":".join(p)
            buffer.append(x)

        print("".join(buffer), file=nw_fo)


def attotree(fns, output_fo, k, s, t, phylogeny_algorithm, fof):
    with tempfile.TemporaryDirectory() as d:
        message('created a temporary directory', d)
        phylip_fn = os.path.join(d, "distances.phylip")
        newick_fn = os.path.join(d, "tree.nw")
        mash_triangle(fns, phylip_fn, k=k, s=s, t=t, fof=fof)
        quicktree(phylip_fn, newick_fn, algorithm=phylogeny_algorithm)
        postprocess_quicktree_nw(newick_fn, output_fo)


def main():

    class CustomArgumentParser(argparse.ArgumentParser):

        def print_help(self):
            msg = self.format_help()
            repl = re.compile(r'\]\s+\[')
            msg = repl.sub("] [", msg)
            msg = msg.replace(" [-h] [-v]", "")
            msg = msg.replace(", --help", "        ")
            print(msg)

        def format_help(self):
            formatter = self._get_formatter()
            formatter.add_text(" \n" + self.description)
            formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)
            formatter.add_text(self.epilog)

            # positionals, optionals and user-defined groups
            for action_group in self._action_groups:
                formatter.start_section(action_group.title)
                formatter.add_text(action_group.description)
                formatter.add_arguments(action_group._group_actions)
                formatter.end_section()

            return formatter.format_help()

    parser = CustomArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Program: {} ({})\n".format(PROGRAM, DESC) + "Version: {}\n".format(VERSION) +
        "Author:  Karel Brinda <karel.brinda@inria.fr>",
    )
    parser.add_argument(
        '-v',
        action='version',
        version='{} {}'.format(PROGRAM, VERSION),
    )

    parser.add_argument(
        '-k',
        type=int,
        metavar='INT',
        dest='k',
        default=DEFAULT_K,
        help=f'kmer size [{DEFAULT_K}]',
    )

    parser.add_argument(
        '-s',
        type=int,
        metavar='INT',
        dest='s',
        default=DEFAULT_S,
        help=f'sketch size [{DEFAULT_S}]',
    )

    parser.add_argument(
        '-t',
        type=int,
        metavar='INT',
        dest='t',
        default=DEFAULT_T,
        help=f'number of threads [{DEFAULT_T}]',
    )

    parser.add_argument(
        '-o',
        metavar='FILE',
        dest='o',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help=f'newick output [stdout]',
    )

    parser.add_argument(
        '-f',
        metavar='STR',
        dest='f',
        default=DEFAULT_F,
        choices=("nj", "upgma"),
        help=f'tree inference algorithm (nj/upgma) [{DEFAULT_F}]',
    )

    parser.add_argument(
        '-L',
        action='store_true',
        dest='L',
        help=f'input files are list of files',
    )

    parser.add_argument(
        'genomes',
        nargs="+",
        help='input genome file (fasta / gzipped fasta / list of files when "-L")',
    )

    args = parser.parse_args()

    print(args)
    attotree(fns=args.genomes, k=args.k, s=args.s, t=args.t, output_fo=args.o, phylogeny_algorithm=args.f, fof=args.L)

    args = parser.parse_args()


if __name__ == "__main__":
    main()
