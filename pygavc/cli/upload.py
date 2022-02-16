import argparse

from ..commands.uploader import Uploader

################################################################################
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--upload",
        required=True,
        action="append",
        help="List of files to upload (required). Expected format is: <classifier>[.<ext>]:<filepath>"
    )

    parser.add_argument(
        "target",
        nargs=1,
        help="Gavc target."
    )

    args = parser.parse_args()

    print(" - Uploads: %s" % repr(args.upload))
    print(" - Gavc: %s" % repr(args.target))

    Uploader(args.target[0], args.upload)()


################################################################################
if __name__ == "__main__":
    main()
