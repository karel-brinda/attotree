#! /usr/bin/env python3

import argparse
import collections
import datetime
import os
import psutil
import re
import subprocess
import sys
import tempfile
import time

from pathlib import Path
from xopen import xopen
from pprint import pprint



log_file = None


def error(*msg, error_code=1):
    print('attotree error:', *msg, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    #close_log()
    sys.exit(error_code)


def message(*msg, subprogram='', upper=False):
    """Print a message to stderr.

    Args:
        *msg: Message.
        subprogram (str): Subprogram.
        upper (bool): Transform text to upper cases.
    """

    #global log_file

    dt = datetime.datetime.now()
    fdt = dt.strftime("%Y-%m-%d %H:%M:%S")

    if upper:
        msg = map(str, msg)
        msg = map(str.upper, msg)

    log_line = '[attotree{}] {} {}'.format(subprogram, fdt, " ".join(msg))

    #if not only_log:
    #    print(log_line, file=sys.stderr)
    #if log_file is not None:
    #    log_file.write(log_line)
    #    log_file.write("\n")
    #    log_file.flush()



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

    ps_p = psutil.Process(p.pid)

    max_rss = 0
    error_code = None
    while error_code is None:
        try:
            max_rss = max(max_rss, ps_p.memory_info().rss)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, OSError, IOError):
            pass
        #except psutil.NoSuchProcess as e:
        #    print("[prophylelib] Warning: psutil - NoSuchProcess (pid: {}, name: {}, msg: {})".format(e.pid, e.name, e.msg), file=sys.stderr)

        # wait 0.2 s
        time.sleep(0.2)
        error_code = p.poll()

    out_fo.flush()

    mem_mb = round(max_rss / (1024 * 1024.0), 1)

    if output_fn is not None:
        out_fo.close()

    if error_code == 0 or error_code == 141:
        if not silent:
            message("Finished ({} MB used): {}".format(mem_mb, command_str))
    else:
        message("Unfinished, an error occurred (error code {}, {} MB used): {}".format(error_code, mem_mb, command_str))

        if err_msg is not None:
            print('Error: {}'.format(err_msg), file=sys.stderr)

        if thr_exc:
            error("A command failed, see messages above.")

        sys.exit(1)


def mash_triangle(p, k=21, s=10000):
    with tempfile.TemporaryDirectory() as tmp_d:
        o=os.path.join(tmp_d, "triangle.txt.xz")
        cmd=f"mash triangle -k {k} -s {s} -p {p} | xz -9 > {o}"
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
