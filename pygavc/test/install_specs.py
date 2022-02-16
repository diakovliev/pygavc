import os
import unittest

from ..valhalla.install_specs import InstallSpecs

TEST_DATA = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), "data", os.path.basename(__file__))

class InstallSpecsTest(unittest.TestCase):
    def test(self):
        files = [
            'dob2pe_sdk.yaml',
            'emscripten_sdk.yaml',
            'oemsdk.yaml',
            'tizen_webapp_sdk.yaml',
        ]

        for filename in files:
            InstallSpecs.load(os.path.join(TEST_DATA, filename))

if __name__ == "__main__":
    unittest.main()
