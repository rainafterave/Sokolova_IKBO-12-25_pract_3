"""Command-line assembler and interpreter for variant 23."""

import argparse
from pathlib import Path
import sys

from assembler import parse_program
from instructions import MachineError


def assemble(args):
    """Print intermediate fields in the stage-one testing mode."""
    program = parse_program(args.source.read_text(encoding="utf-8-sig"))
    if args.test:
        for instruction in program:
            print(", ".join(
                f"{key}={value}" for key, value in instruction.fields().items()
            ))


def main(argv=None):
    """Parse command-line arguments and report input errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compiler = commands.add_parser("assemble", help="assemble a source file")
    compiler.add_argument("source", type=Path)
    compiler.add_argument("-o", "--output", type=Path, required=True)
    compiler.add_argument("--test", action="store_true")
    compiler.set_defaults(action=assemble)
    args = parser.parse_args(argv)
    try:
        args.action(args)
    except (MachineError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
