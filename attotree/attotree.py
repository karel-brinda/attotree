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
import time

sys.path.append(os.path.dirname(__file__))
import version

PROGRAM = 'attotree'
VERSION = version.VERSION
DESC = 'rapid estimation of phylogenetic tree using sketching'

DEFAULT_S = 10000
DEFAULT_K = 21
DEFAULT_T = os.cpu_count()


def error(*msg, error_code=1):
    print('attotree error:', *msg, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    #close_log()
    sys.exit(error_code)


def message(*msg):
    dt = datetime.datetime.now()
    fdt = dt.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f'[attotree] {fdt} {msg}'
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


def mash_triangle(p, k=21, s=10000):
    with tempfile.TemporaryDirectory() as tmp_d:
        o = os.path.join(tmp_d, "triangle.txt.xz")
        cmd = f"mash triangle -k {k} -s {s} -p {p} | xz -9 > {o}"
        message("Running mash triangle, printing output to", o)
        run_safe(cmd)
    return


def convert_to_phylip(triangle_fn, phylip, rescale=False):
    # todo: rescale
    """
    xzcat {input.triangle} \\
        | perl -pe 's/\.(fa|fasta)//g' \\
        | xz -9 -T1 \\
        > {output.phylip}
    ./triangle_to_square.py {input.triangle} \\
        | xz -9 -T1 \\
        > {output.distmap}
    ./scale_phylip.py -f {params.scaling_factor} {input.phylip} \\
        | xz -9 -T1  \\
        > {output.phylip}

    """
    """
    (
        cd assemblies
        mash triangle -p 7 GCGS*.fa \
    ) \
        | perl -pe 's/\.(fa|fasta)//g' \
        > _gono_dist.phylip

    quicktree -in m _gono_dist.phylip \
        > gono_mashquicktree-nonlad.nw
    """
    pass


def mash_triangle(inp_fns, phylip_fn, k, s, t):
    cmd = f"mash triangle -s {s} -k {k} -p {t}".split() + inp_fns
    run_safe(cmd, output_fn=phylip_fn)


def quicktree(phylip_fn, newick_fn):
    cmd = "quicktree -in m".split() + [phylip_fn]
    run_safe(cmd, output_fn=newick_fn)


def postprocess_quicktree_nw(nw1, nw2):
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

    with open(nw2, "w") as fo:
        print("".join(buffer), file=fo)


def attotree(fns, k, s, t):
    phylip_fn = "a.phylip"
    newick_fn1 = "a.nw0"
    newick_fn2 = "a.nw"
    mash_triangle(fns, phylip_fn, k=k, s=s, t=t)
    quicktree(phylip_fn, newick_fn1)
    postprocess_quicktree_nw(newick_fn1, newick_fn2)


def main():

    class CustomArgumentParser(argparse.ArgumentParser):

        def print_help(self):
            msg = self.format_help()
            msg = msg.replace("usage:", "Usage:  ")
            for x in 'PY_EXPR', 'PY_CODE':
                msg = msg.replace("[{x} [{x} ...]]\n            ".format(x=x), x)
                msg = msg.replace("[{x} [{x} ...]]".format(x=x), x)
            repl = re.compile(r'\]\s+\[')
            msg = repl.sub("] [", msg)
            msg = msg.replace("\n  -0", "\n\nAdvanced options:\n  -0")
            msg = msg.replace(" [-h] [-v]", "")
            msg = msg.replace("[-0", "\n                    [-0")
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
        '--version',
        action='version',
        version='{} {}'.format(PROGRAM, VERSION),
    )

    parser.add_argument(
        '-k',
        '--kmer-lenght',
        type=int,
        metavar='INT',
        dest='k',
        default=DEFAULT_K,
        help=f'kmer size [{DEFAULT_K}]',
    )

    parser.add_argument(
        '-s',
        '--sketch-size',
        type=int,
        metavar='INT',
        dest='s',
        default=DEFAULT_S,
        help=f'sketch size [{DEFAULT_S}]',
    )

    parser.add_argument(
        '-t',
        '--threads',
        type=int,
        metavar='INT',
        dest='t',
        default=DEFAULT_T,
        help=f'number of threads [{DEFAULT_T}]',
    )

    parser.add_argument(
        'inp_fa',
        nargs="+",
        help='',
    )

    args = parser.parse_args()

    attotree(fns=args.inp_fa, k=args.k, s=args.s, t=args.t)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
