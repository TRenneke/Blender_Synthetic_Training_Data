import unittest
import sdg_utils

class TestUtils(unittest.TestCase):
    def test_sampler_from_string(self):
        # Test list of tuples
        input_string = "Uniform(0, 1)"
        output: sdg_utils.Sampler = sdg_utils.sampler_from_string(input_string, sdg_utils.float_parser)
        self.assertEqual(output.min(), 0)
        self.assertEqual(output.max(), 1)


        input_string = "Choice([Hallo, Welt])"
        output: sdg_utils.ChoiceSampler = sdg_utils.sampler_from_string(input_string, sdg_utils.str_parser)
        self.assertEqual(output.values(), ["Hallo", "Welt"])

        input_string = "Choice([Uniform((0, 0, 0), (1, 1, 1)), (2, 1)])"
        output: sdg_utils.ChoiceSampler = sdg_utils.sampler_from_string(input_string, sdg_utils.float_parser)
        sample = output.values()
        self.assertEqual(sample[1], (2, 1))
        self.assertTrue(0 <= sample[0][0] <= 1 and 0 <= sample[0][1] <= 1 and 0 <= sample[0][2] <= 1)

        input_string = "Choice([Uniform((0, 0, 0), (1, 1, 1)), (2, 1)], 2)"
        output: sdg_utils.ChoiceSampler = sdg_utils.sampler_from_string(input_string, sdg_utils.float_parser)
        

        rand = sdg_utils.Randomization.from_file("TEST/test.yaml")
if __name__ == "__main__":
    unittest.main()
T