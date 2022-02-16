import unittest
import os

from ..valhalla.build_config import BuildConfig

TEST_DATA = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), "data", os.path.basename(__file__))

class BuildConfigTests(unittest.TestCase):
    def test(self):

        config = BuildConfig.load(os.path.join(TEST_DATA, "charter-humaxwb20-powerup-prd.yaml"))

        self.assertEqual("prd", config.get_arg("build_variant"))
        self.assertEqual("charter.worldbox20.oemsdk.release:humaxwb20:16.2.+", config.get_arg("oemsdk_gavc"))
        self.assertEqual("dob2pe_sdk.valhalla_bv3_trunk:DOB2PE_SDK:+", config.get_arg("dob2pe_sdk_gavc"))

if __name__ == "__main__":
    unittest.main()
