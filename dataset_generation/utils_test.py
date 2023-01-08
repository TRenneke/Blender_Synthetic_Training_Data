import unittest
import utils

class TestUtils(unittest.TestCase):
    def test_sampler_from_string(self):
        # Test list of tuples
        input_string = "Uniform(0, 1)"
        output: utils.Sampler = utils.sampler_from_string(input_string, utils.float_parser)
        self.assertEqual(output.min.sample(), 0)
        self.assertEqual(output.max.sample(), 1)


        input_string = "Choice([Hallo, Welt])"
        output: utils.ChoiceSampler = utils.sampler_from_string(input_string, utils.str_parser)
        self.assertEqual(output.values.sample(), ["Hallo", "Welt"])

        input_string = "Choice([Uniform((0, 0, 0), (1, 1, 1)), (2, 1)])"
        output: utils.ChoiceSampler = utils.sampler_from_string(input_string, utils.float_parser)
        sample = output.values.sample()
        self.assertEqual(sample[1], (2, 1))
        self.assertTrue(0 <= sample[0][0] <= 1 and 0 <= sample[0][1] <= 1 and 0 <= sample[0][2] <= 1)


if __name__ == "__main__":
    unittest.main()
T