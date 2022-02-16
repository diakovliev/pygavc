################################################################################
class YamlUtils:
    @staticmethod
    def have_key(y, key):
        return key in y and y[key]

    @staticmethod
    def val2str(v):
        if type(v) is bool:
            return 'true' if v else 'false'

        if type(v) is str:
            return "\"%s\"" % v

        if type(v) is list:
            return "\"%s\"" % (','.join(v))

        return repr(v)
