import argparse

from .pydab import PyDab


def parse_args():
    parser = argparse.ArgumentParser(
        description="Converting network data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        metavar="",
        help="Input file path.",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        metavar="",
        help="Output file path.",
    )

    parser.add_argument(
        "-ll",
        "--log_level",
        default="WARNING",
        metavar="",
        help="Log level.",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress verbosity, same as setting log_level to CRITICAL.",
    )

    args = parser.parse_args()
    args.log_level = "CRITICAL" if args.quiet else args.log_level

    return args


def main():
    args = parse_args()

    pdb = PyDab(args.input, log_level=args.log_level)
    pdb.export(args.output)
