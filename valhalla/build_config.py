#! /usr/bin/env python

import os
import argparse
import yaml
import copy
import re

from .yaml_utils import YamlUtils

class ValueHelper:
    @staticmethod
    def decode(value):
        if value is None: return value
        return value[1:-1] if value.startswith("\"") else value


class BuildConfig:

    ENV         = "env"
    ARGS        = "args"
    EXTERNALS   = "externals"

    # Deps collections
    SYSROOT     = "sysroot"
    NFS         = "nfs"
    DOCS        = "docs"
    CDS_GROUP   = "cds_group"

    PARTITIONS  = "partitions"
    PART_PFX    = "partition_"
    PART_SEPA   = ':'

    ALL         = [ ENV, ARGS, SYSROOT, NFS, DOCS, CDS_GROUP, EXTERNALS, PARTITIONS ]

    # import operator
    IMPORT      = "import"

    def __init__(self):
        self.env        = dict()
        self.args       = dict()
        self.externals  = dict()

        self.sysroot    = list()
        self.nfs        = list()
        self.docs       = list()
        self.cds_group  = list()
        self.partitions = list()

    def get_arg(self, arg):
        return ValueHelper.decode(self.args.get(arg))

    def get_env(self, env):
        return ValueHelper.decode(self.env.get(env))

    def load_env(self, yf):
        if not YamlUtils.have_key(yf, self.ENV):
            return

        for (k,v) in yf[self.ENV].items():
            self.env[k] = v

    def load_args(self, yf):
        if not YamlUtils.have_key(yf, self.ARGS):
            return

        for (k,v) in yf[self.ARGS].items():
            self.args[k] = YamlUtils.val2str(v)

    def load_externals(self, yf):
        if not YamlUtils.have_key(yf, self.EXTERNALS):
            return

        for (k,v) in yf[self.EXTERNALS].items():
            self.externals[k] = v

    def load_deps_collection(self, yf, collection_ref, collection_name):
        if not YamlUtils.have_key(yf, collection_name):
            return

        for d in yf[collection_name]:
            collection_ref.append(d)

    def load_sysroot(self, yf):
        self.load_deps_collection(yf, self.sysroot, self.SYSROOT)

    def load_nfs(self, yf):
        self.load_deps_collection(yf, self.nfs, self.NFS)

    def load_docs(self, yf):
        self.load_deps_collection(yf, self.docs, self.DOCS)

    def load_cds_group(self, yf):
        self.load_deps_collection(yf, self.cds_group, self.CDS_GROUP)

    def load_partitions(self, yf):
        self.partitions = []
        if not YamlUtils.have_key(yf, self.PARTITIONS):
            return

        for (k,v) in yf[self.PARTITIONS].items():
            assert k.startswith(self.PART_PFX)
            part_no = k[len(self.PART_PFX):]
            for r in v:
                self.partitions.append(part_no + self.PART_SEPA + r)

    def merge(self, rhs):
        result = BuildConfig()

        result.env              = copy.copy(self.env)
        for k,v in rhs.env.items():
            result.env[k]       = v

        result.args             = copy.copy(self.args)
        for k,v in rhs.args.items():
            result.args[k]      = v

        result.externals        = copy.copy(self.externals)
        for k,v in rhs.externals.items():
            result.externals[k] = v

        # Deps collections
        result.sysroot          = copy.copy(self.sysroot)
        result.sysroot.extend(rhs.sysroot)
        result.sysroot          = list(set(result.sysroot))

        result.nfs              = copy.copy(self.nfs)
        result.nfs.extend(rhs.nfs)
        result.nfs              = list(set(result.nfs))

        result.docs             = copy.copy(self.docs)
        result.docs.extend(rhs.docs)
        result.docs             = list(set(result.docs))

        result.cds_group        = copy.copy(self.cds_group)
        result.cds_group.extend(rhs.cds_group)
        result.cds_group        = list(set(result.cds_group))

        # Partitions map
        result.partitions       = copy.copy(self.partitions)
        for rhs_item in rhs.partitions:
            rhs_kv = rhs_item.split(self.PART_SEPA)
            for lhs_item in result.partitions:
                lhs_kv = lhs_item.split(self.PART_SEPA)
                if rhs_kv[1] == lhs_kv[1]:
                    result.partitions.remove(lhs_item)

        result.partitions.extend(rhs.partitions)
        result.partitions       = list(set(result.partitions))

        return result

    @staticmethod
    def parse_import(import_val):
        import_arr = import_val.split(':', 1)
        path = import_arr[0]

        what = list()
        if len(import_arr) < 2:
            what.extend(BuildConfig.ALL)
        else:
            what.extend(import_arr[1].split('|'))

        return path, what

    @staticmethod
    def make_exception(parents, config_path, message, e = None):
        msg = "%s: %s" % (config_path, message)
        if parents:
            for p in parents:
                msg += "\n\timported from: %s" % p
        if e:
            msg += "\n\tcaused by:\n%s" % e

        return Exception(msg)

    @staticmethod
    def load(config_path, what = ALL, parents = None, callback = None):
        yf = None

        if not os.path.exists(config_path):
            raise BuildConfig.make_exception(parents, config_path, "Configuration file doesn't exist!")

        try:
            with open(config_path, 'r') as f:
                yf = yaml.safe_load(f)

        except Exception as e:
            raise BuildConfig.make_exception(parents, config_path, "Unable to load configuration file!", e)

        assert yf != None, "yf == None!"

        if callback:
            callback(config_path)

        base_config = None
        if YamlUtils.have_key(yf, BuildConfig.IMPORT):
            base_config = BuildConfig()

            configs_to_import = []

            imported_val = yf[BuildConfig.IMPORT]
            if type(imported_val) == list:
                configs_to_import.extend(imported_val)
            elif type(imported_val) == str:
                configs_to_import.append(imported_val)
            else:
                raise BuildConfig.make_exception(
                    parents,
                    config_path,
                    "Import value must be string or list! The %s is %s instead!" % (imported_val, type(imported_val))
                )

            config_parent_dir = os.path.dirname(os.path.normpath(config_path))
            for ic in configs_to_import:

                import_path, import_what = BuildConfig.parse_import(ic)

                if parents:
                    curr_parents = copy.copy(parents)
                    curr_parents.insert(0, config_path)
                else:
                    curr_parents = [ config_path ]

                for w in import_what:
                    if not w in BuildConfig.ALL:
                        raise BuildConfig.make_exception(parents, config_path, "Wrong import spec: '%s'! The '%s' is unknown configuration file part to load!" % (ic, w))

                base_config = base_config.merge(BuildConfig.load(config_parent_dir + "/" + import_path, import_what, curr_parents, callback))

        config = BuildConfig()
        if BuildConfig.ENV in what:
            config.load_env(yf)
        if BuildConfig.ARGS in what:
            config.load_args(yf)
        if BuildConfig.EXTERNALS in what:
            config.load_externals(yf)

        # Deps collections
        if BuildConfig.SYSROOT in what:
            config.load_sysroot(yf)
        if BuildConfig.NFS in what:
            config.load_nfs(yf)
        if BuildConfig.DOCS in what:
            config.load_docs(yf)
        if BuildConfig.CDS_GROUP in what:
            config.load_cds_group(yf)

        # Partitions map
        if BuildConfig.PARTITIONS in what:
            config.load_partitions(yf)

        if base_config:
            config = base_config.merge(config)

        return config

    def store(self, output):
        config = dict()

        config[self.ENV]         = self.env
        config[self.ARGS]        = self.args
        config[self.EXTERNALS]   = self.externals

        # Deps collections
        config[self.SYSROOT]     = self.sysroot
        config[self.NFS]         = self.nfs
        config[self.DOCS]        = self.docs
        config[self.CDS_GROUP]   = self.cds_group

        # Store partitions map
        config[self.PARTITIONS]  = dict()
        for item in self.partitions:
            kv = item.split(self.PART_SEPA)
            curr_collection = self.PART_PFX + kv[0]

            if not curr_collection in config[self.PARTITIONS]:
                config[self.PARTITIONS][curr_collection] = list()

            config[self.PARTITIONS][curr_collection].append(kv[1])

        default_flow_style_val = False
        if output:
            with open(output, "w") as f:
                return yaml.dump(config, f, default_flow_style=default_flow_style_val)
        else:
            return yaml.dump(config, None, default_flow_style=default_flow_style_val)
