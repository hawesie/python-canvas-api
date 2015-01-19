import unittest

import marking_actions


class TestMarkingFunctions(unittest.TestCase):
    def test_usernames(self):
        # only works on student usernames
        self.assertFalse(marking_actions.is_username('nah'))
        self.assertFalse(marking_actions.is_username('hawesna'))
        # like these
        self.assertTrue(marking_actions.is_username('abc123'))
        self.assertTrue(marking_actions.is_username('nia411'))
        self.assertTrue(marking_actions.is_username('hbe173'))
        # and these
        self.assertTrue(marking_actions.is_username('ABD123'))
        self.assertTrue(marking_actions.is_username('ASD411'))
        self.assertTrue(marking_actions.is_username('XXX173'))
        #
        self.assertFalse(marking_actions.is_username('a123'))
        self.assertFalse(marking_actions.is_username('123abc'))
        self.assertFalse(marking_actions.is_username('abc1'))


if __name__ == '__main__':
    unittest.main()