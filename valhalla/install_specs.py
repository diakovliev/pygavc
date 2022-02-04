import os
import yaml

class InstallSpecs:
    INSTALLS        = 'installs'
    GAVC            = 'gavc'
    GAVC_ARG        = 'gavc_arg'
    ROOT_PREFIX_ARG = 'root_prefix_arg'
    ROOT_DIR        = 'root_dir'
    SPECS           = 'specs'
    SPEC_SEPA       = ':'

    class Spec:
        def __init__(self, classifier, destination_dir):
            self.__classifier       = classifier
            self.__destination_dir  = destination_dir

        @staticmethod
        def parse(input_string):
            classifier      = input_string
            destination_dir = ""
            if InstallSpecs.SPEC_SEPA in classifier:
                parts = classifier.split(InstallSpecs.SPEC_SEPA, 1)
                classifier      = parts[0]
                destination_dir = parts[1]
            return InstallSpecs.Spec(classifier, destination_dir)

        def classifier(self):
            return self.__classifier

        def destination_dir(self):
            return self.__destination_dir


    class Install:
        def __init__(self, gavc, gavc_arg, root_prefix_arg, root_dir, specs):
            self.__gavc            = gavc
            self.__gavc_arg        = gavc_arg
            self.__root_dir        = root_dir
            self.__root_prefix_arg = root_prefix_arg
            self.__specs           = specs

        @staticmethod
        def load(input_object):
            assert InstallSpecs.GAVC in input_object or InstallSpecs.GAVC_ARG in input_object
            assert InstallSpecs.ROOT_DIR in input_object
            assert InstallSpecs.SPECS in input_object

            gavc        = ""
            gavc_arg    = ""
            if InstallSpecs.GAVC in input_object:
                gavc = input_object[InstallSpecs.GAVC]
                assert not InstallSpecs.GAVC_ARG in input_object
            else:
                gavc_arg = input_object[InstallSpecs.GAVC_ARG]
                assert not InstallSpecs.GAVC in input_object

            root_dir = input_object[InstallSpecs.ROOT_DIR]
            root_prefix_arg = None
            if InstallSpecs.ROOT_PREFIX_ARG in input_object:
                root_prefix_arg = input_object[InstallSpecs.ROOT_PREFIX_ARG]

            specs = []
            for spec_str in input_object[InstallSpecs.SPECS]:
                specs.append(InstallSpecs.Spec.parse(spec_str))

            return InstallSpecs.Install(gavc, gavc_arg, root_prefix_arg, root_dir, specs)

        def gavc(self):
            return self.__gavc

        def gavc_arg(self):
            return self.__gavc_arg

        def root_dir(self):
            return self.__root_dir

        def root_prefix_arg(self):
            return self.__root_prefix_arg

        def specs(self):
            return self.__specs


    def __init__(self, installs):
        self.__installs = installs

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            o = yaml.safe_load(f)

        assert InstallSpecs.INSTALLS in o

        installs = []
        for install in o[InstallSpecs.INSTALLS]:
            installs.append(InstallSpecs.Install.load(install))

        return InstallSpecs(installs)

    def installs(self):
        return self.__installs