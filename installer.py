import os
import argparse
import zipfile
import tqdm

from gavc.query import Query
from gavc.artifactory_client import ArtifactoryClient
from gavc.fs_utils import FsUtils
from valhalla.install_specs import InstallSpecs
from valhalla.build_config import BuildConfig

class Installer:
    def __init__(self, install_specs, build_config = None):
        self.__install_specs    = install_specs
        self.__build_config     = build_config
        self.__client           = ArtifactoryClient()


    def __resolve_version(self, query):
        versions = self.__client.requests().metadata_for(query).versions_for(query)
        assert len(versions) == 1
        return versions[0]


    def install(self, install_root):
        print(" - Install into '%s'" % install_root)

        for install in self.__install_specs.installs():

            gavc = None
            if install.gavc_arg():
                assert self.__build_config is not None, "Build config is not set!"
                gavc = self.__build_config.get_arg(install.gavc_arg())
                print(" -- arg: '%s' gavc: '%s'" % (install.gavc_arg(), gavc))
                # assert gavc is not None, "Gavc got from the build config by arg '%s' is None!" % install.gavc_arg()
            else:
                gavc = install.gavc()
                print(" -- gavc: '%s'" % gavc)

            # assert gavc is not None
            if not gavc:
                continue

            root_prefix = ""
            if install.root_prefix_arg():
                assert self.__build_config is not None, "Build config is not set!"
                root_prefix = self.__build_config.get_arg(install.root_prefix_arg())
                print(" -- arg: '%s' root_prefix: '%s'" % (install.root_prefix_arg(), root_prefix))
                assert root_prefix is not None, "Root prefix got from the build config by arg '%s' is None!" % install.root_prefix_arg()

            main_query  = Query.parse(gavc)
            print(" -- Main query: '%s'" % main_query)
            print(" -- Root dir: '%s'" % install.root_dir())

            element_install_root = os.path.join(install_root, root_prefix, install.root_dir())
            print(" -- Element install root: '%s'" % element_install_root)

            res_version = self.__resolve_version(main_query)
            print(" -- Resolved version: '%s'" % res_version)

            for spec in install.specs():

                print(" --- Classifier: '%s'" % spec.classifier())
                print(" --- Destination dir: '%s'" % spec.destination_dir())

                destination_dir = os.path.join(element_install_root, spec.destination_dir())
                print(" --- Final destination dir: '%s'" % destination_dir)

                subquery = main_query.make_subquery(version=res_version, classifier=spec.classifier())

                print(" --- Sub query: '%s'" % subquery)
                for asset in  self.__client.requests().assets_for(subquery):
                    with self.__client.requests().retrieve_asset(asset) as cache_access_wrapper:
                        with FsUtils.directory_lock(FsUtils.ensure_dir(destination_dir)):
                            print(" --- Extract archive into: '%s'..." % destination_dir)
                            with zipfile.ZipFile(cache_access_wrapper.path(), 'r') as zip_ref:
                                for archive_file in tqdm.tqdm(iterable=zip_ref.namelist(), total=len(zip_ref.namelist())):
                                    zip_ref.extract(member=archive_file, path=destination_dir)


        print(" - Clean objects cache")
        self.__client.cache().objects().clean()

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
        Installer(InstallSpecs.load(specs_file), build_config).install(args.destination_dir)


if __name__ == "__main__":
    main()
