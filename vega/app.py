import sys
import argparse

from .smtlib.app import evaluate_smt2_file

def usage(parser):
    parser.print_help(sys.stderr)
    sys.exit(1)

def main():
    version = "TODO" # TODO: load from setup.py or something else

    parser = argparse.ArgumentParser(description='vega [version {}] (c) Copyright 2020 TomoriNao (@K_atc).'.format(version))
    parser.add_argument("-smt2", action="store_true", default=True, help='use parser for SMT 2 input format (default: true)')
    parser.add_argument("-in", dest="_in", action="store_true", help='read formula from standard input')
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    if args.smt2:
        if args._in:
            evaluate_smt2_file(sys.stdin)
        else:
            if args.file:
                with open(args.file) as f:
                    evaluate_smt2_file(f)
            else:
                print("[!] Specify `file`")
                usage(parser)

    