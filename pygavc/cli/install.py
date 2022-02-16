import argparse

from ..valhalla.install_specs import InstallSpecs
from ..valhalla.build_config import BuildConfig
from ..commands.installer import Installer

################################################################################
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--install_specs_file",
        required=True,
        action="append",
        help="Install specs file(s) to process.",
    )

    parser.add_argument(
        "--destination_dir",
        required=True,
        action="store",
        help="Install destination directory.",
    )

    parser.add_argument(
        "--build_config_file",
        action="store",
        help="Valhalla target configuration file.",
    )

    args = parser.parse_args()

    build_config = None
    if args.build_config_file:
        print(" - Load '%s'" % args.build_config_file)
        build_config = BuildConfig.load(args.build_config_file)

    for specs_file in args.install_specs_file:
        print(" - Process '%s'" % specs_file)
        Installer(InstallSpecs.load(specs_file), build_config)(args.destination_dir)



################################################################################
if __name__ == "__main__":
    main()
