import unittest

import day22


class Test1DIntervalContainers(unittest.TestCase):

    def test_interval_setup(self):
        test_IC = day22.IntervalContainer(10, 12)
        self.assertEqual(test_IC.first, test_IC.last)
        self.assertEqual(10, test_IC.first.start)
        self.assertEqual(12, test_IC.first.stop)

    def test_addition(self):
        test_IC = day22.IntervalContainer(10, 12)
        test_IC.update(True, 11, 13)
        self.assertEqual(test_IC.first.start, 10)
        self.assertEqual(test_IC.first.stop, 13)
        self.assertEqual(test_IC.first, test_IC.last)
        pass

    def test_subtraction(self):
        test_IC = day22.IntervalContainer(10, 13)
        test_IC.update(False, 9, 11)
        self.assertEqual(test_IC.first.start, 12)
        self.assertEqual(test_IC.first, test_IC.last)

    def test_splitting(self):
        test_IC = day22.IntervalContainer(10, 13)
        test_IC.update(False, 11, 11)
        self.assertEqual(10, test_IC.first.start)
        self.assertEqual(10, test_IC.first.stop)
        self.assertEqual(12, test_IC.last.start)
        self.assertEqual(13, test_IC.last.stop)

    def test_joining(self):
        test_IC = day22.IntervalContainer(10, 13)
        test_IC.update(False, 11, 11)
        test_IC.update(True, 11, 11)
        self.assertEqual(10, test_IC.first.start)
        self.assertEqual(13, test_IC.first.stop)


class Test2DIntervalContainers(unittest.TestCase):

    def test_2d_setup(self):
        test_IC = day22.IntervalContainer(10, 12, 10, 12, 10, 12)
        self.assertEqual(10, test_IC.first.start)
        self.assertEqual(12, test_IC.first.stop)
        self.assertEqual(10, test_IC.first.subcontainer.first.start)
        self.assertEqual(12, test_IC.first.subcontainer.first.stop)
        self.assertEqual(10, test_IC.first.subcontainer.first.subcontainer.first.start)
        self.assertEqual(12, test_IC.first.subcontainer.first.subcontainer.first.stop)

    def test_addition_2d(self):
        test_IC = day22.IntervalContainer(10, 12, 10, 12, 10, 12)
        test_IC.update(True, 11, 13, 11, 13, 11, 13)
        self.assertEqual(10, test_IC.first.start)
        self.assertEqual(13, test_IC.first.stop)
        self.assertEqual(10, test_IC.first.subcontainer.first.start)
        self.assertEqual(13, test_IC.first.subcontainer.first.stop)
        self.assertEqual(10, test_IC.first.subcontainer.first.subcontainer.first.start)
        self.assertEqual(13, test_IC.first.subcontainer.first.subcontainer.first.stop)

    def test_subtraction_2d(self):
        test_IC = day22.IntervalContainer(10, 12, 10, 12, 10, 12)
        test_IC.update(False, 9, 11, 9, 11, 9, 11)
        pass


if __name__ == '__main__':
    unittest.main()
