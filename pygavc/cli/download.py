import argparse

from ..commands.downloader import Downloader

################################################################################
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        action="store",
        help="Output file."
    )

    parser.add_argument(
        "target",
        nargs=1,
        help="Gavc target."
    )

    args = parser.parse_args()

    print(" - Gavc: %s" % args.target)
    print(" - Output: %s" % args.output)

    Downloader(args.target[0])(args.output)


################################################################################
if __name__ == "__main__":
    main()
