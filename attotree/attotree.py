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


def shorten_output(s):
    # return pprint.pformat(s)
    if len(s) > 40:
        s = s[:40] + "..."
    return s


def error(*msg, error_code=1):
    """
    Prints an error message to stderr and exits the program with the specified error code.

    Args:
        *msg: Variable number of message arguments to be printed.
        error_code (int): The error code to exit the program with. Default is 1.
    """
    print('attotree error:', *msg, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    #close_log()
    sys.exit(error_code)


def message(*msg):
    """
    Prints a log message with a timestamp.

    Args:
        *msg: Variable number of message strings.

    Returns:
        None
    """
    dt = datetime.datetime.now()
    fdt = dt.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f'[attotree] {fdt} {" ".join(msg)}'
    print(log_line, file=sys.stderr)


def run_safe(command, output_fn=None, output_fo=None, err_msg=None, thr_exc=True, silent=False, verbose=True):
    """
    Executes a shell command safely.

    Args:
        command (list): The shell command to be executed, as a list of strings.
        output_fn (str, optional): The filename to redirect the command's output to. Defaults to None.
        output_fo (file object, optional): The file object to redirect the command's output to. Defaults to None.
        err_msg (str, optional): The error message to be displayed if the command fails. Defaults to None.
        thr_exc (bool, optional): Whether to raise an exception if the command fails. Defaults to True.
        silent (bool, optional): Whether to suppress the output of the command. Defaults to False.

    Raises:
        SystemExit: If the command fails and `thr_exc` is True.

    Returns:
        None
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
    if verbose:
        command_str_nice = command_str
    else:
        command_str_nice = shorten_output(command_str)

    if not silent:
        message(f"Shell command: '{command_str_nice}'")

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
            message(f"Finished: '{command_str_nice}'")
    else:
        message(f"Unfinished, an error occurred (error code {error_code}): '{command_str}'")

        if err_msg is not None:
            print('Error: {}'.format(err_msg), file=sys.stderr)

        if thr_exc:
            error("A command failed, see messages above.")

        sys.exit(1)


def mash_triangle(inp_fns, phylip_fn, k, s, t, fof, verbose):
    """
    Runs the 'mash triangle' command with the given parameters.

    Args:
        inp_fns (list): List of input filenames.
        phylip_fn (str): Output filename for the phylip file.
        k (int): Value for the '-k' option.
        s (int): Value for the '-s' option.
        t (int): Value for the '-p' option.
        fof (bool): Flag indicating whether to use the '-l' option.

    Returns:
        None

    Raises:
        None
    """
    message("Running Mash")
    cmd = f"mash triangle -s {s} -k {k} -p {t}".split()
    if fof:
        cmd += ["-l"]
    cmd += inp_fns
    run_safe(cmd, output_fn=phylip_fn, verbose=verbose)


def fn_to_node_name(fn):
    """
    Converts a file name to a node name by removing the path and file extension.

    Args:
        fn (str): The file name.

    Returns:
        str: The node name without the file extension.
    """
    basename_components = os.path.basename(fn).split(".")
    if len(basename_components) == 1:
        basename_components.append("")
    # remove suffix
    nname = ".".join(basename_components[:-1])
    return nname


def postprocess_mash_phylip(phylip_in_fn, phylip_out_fn, verbose):
    """
    Postprocesses a PHYLIP file by copying its contents from the input file to the output file.

    Args:
        phylip_in_fn (str): The path to the input PHYLIP file.
        phylip_out_fn (str): The path to the output PHYLIP file.

    Returns:
        None
    """
    with open(phylip_in_fn) as f:
        with open(phylip_out_fn, "w+") as g:
            for i, x in enumerate(f):
                x = x.strip()
                if i != 0:
                    l, sep, r = x.partition("\t")
                    l = fn_to_node_name(l)
                    x = l + sep + r
                print(x, file=g)
    #basename_components = os.path.basename(p[0]).split(".")
    #if len(basename_components) == 1:
    #    basename_components.append("")
    ## remove suffix
    #p[0] = ".".join(basename_components[:-1])


def quicktree(phylip_fn, newick_fn, algorithm, verbose):
    """
    Runs the quicktree algorithm to generate a phylogenetic tree.

    Args:
        phylip_fn (str): The filename of the input phylip file.
        newick_fn (str): The filename of the output newick file.
        algorithm (str): The algorithm to use for tree construction. Valid options are "upgma" or "nj".

    Returns:
        None
    """
    message("Running quicktree")

    cmd = "quicktree -in m".split()
    if algorithm == "upgma":
        cmd += ["-upgma"]
    cmd += [phylip_fn]
    run_safe(cmd, output_fn=newick_fn, verbose=verbose)


def postprocess_quicktree_nw(nw_in_fn, nw_out_fo, verbose):
    """
    Reformat newick.

    This function reads an input newick file, removes any leading or trailing whitespace from each line,
    and writes the postprocessed newick file to the specified file object.

    Notes:
    - assumption: node names already don't contain paths and prefixes
    - expects fo to allow both a filename or stdout

    Args:
        nw_in_fn (str): Path to the input newick file.
        nw_out_fo (file object): File object to write the postprocessed newick file.
        verbose (bool): If True, print additional information during the postprocessing.

    Returns:
        None
    """
    message("Postprocessing tree")
    buffer = []
    with open(nw_in_fn) as fo:
        for x in fo:
            x = x.strip()
            buffer.append(x)
    print("".join(buffer), file=nw_out_fo)


def attotree(fns, newick_fo, k, s, t, phylogeny_algorithm, fof, verbose, debug):
    """
    Generate a phylogenetic tree using the given parameters.

    Args:
        fns (list): List of input filenames.
        newick_fo (file object): Output file object to write the generated tree.
        k (int): Value for parameter k.
        s (int): Value for parameter s.
        t (int): Value for parameter t.
        phylogeny_algorithm (str): Name of the phylogeny algorithm to use.
        fof (bool): Flag indicating whether to use the fof parameter.
        verbose (bool): Flag indicating whether to enable verbose output.

    Returns:
        None
    """
    features = []
    if verbose:
        features.append("verbose")
    if debug:
        features.append("debuging")
    if len(features) > 0:
        fmsg = f" ({', '.join(features)})"
    else:
        fmsg = ""
    message(f"Attotree starting{fmsg}")
    with tempfile.TemporaryDirectory(delete=not debug) as d:
        message('Created a temporary directory', d)
        phylip1_fn = os.path.join(d, "distances.phylip0")
        phylip2_fn = os.path.join(d, "distances.phylip")
        newick1_fn = os.path.join(d, "tree.nw")
        newick2_fo = newick_fo
        if fof:
            #This is to make the list of file pass to Mash even with
            #process substitutions
            old_fof_fn = fns[0]
            new_fof_fn = os.path.join(d, "fof.txt")
            with open(old_fof_fn) as f, open(new_fof_fn, 'w') as g:
                g.write(f.read())
            fns = [new_fof_fn]
        mash_triangle(fns, phylip1_fn, k=k, s=s, t=t, fof=fof, verbose=verbose)
        postprocess_mash_phylip(phylip1_fn, phylip2_fn, verbose=verbose)
        quicktree(phylip2_fn, newick1_fn, algorithm=phylogeny_algorithm, verbose=verbose)
        postprocess_quicktree_nw(newick1_fn, newick2_fo, verbose=verbose)

    if debug:
        emsg = f" (auxiliary files retained in '{d}')"
    else:
        emsg = ""
    message(f"Attotree finished{emsg}")


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
        '-D',
        action='store_true',
        dest='D',
        help=f'debugging (don\'t remove tmp dir)',
    )

    parser.add_argument(
        '-V',
        action='store_true',
        dest='V',
        help=f'verbose output',
    )

    parser.add_argument(
        'genomes',
        nargs="+",
        help='input genome file (fasta / gzipped fasta / list of files when "-L")',
    )

    args = parser.parse_args()

    #print(args)
    attotree(
        fns=args.genomes, k=args.k, s=args.s, t=args.t, newick_fo=args.o, phylogeny_algorithm=args.f, fof=args.L,
        verbose=args.V, debug=args.D
    )

    args = parser.parse_args()


if __name__ == "__main__":
    main()
