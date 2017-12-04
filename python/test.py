#! /usr/bin/python
# -*- coding: utf-8 -*-
from jewishdate import JewishDate
from datetime import datetime
import unittest

#!a = hebrew day name (yom rishon)(ithout the word yom)(in heabrew)
#!A = endlish day name (with shabbos)
#!b = hebrew month name
#!B = english jewish month name
#!c = hebrew day as letter (if they want a geresh they can add it)
#!d = 0 padded hebrew day (01 or 19)
#!D = non zero padded hebrew day (1 or 19)
#!e = hebrew day of month in hebrew with geresh
#!E = hebrew day of month in hebrew without geresh
#!m = month number 0 padded
#!M = month number no zero padding
#!y = jewish year hebrew without thousands (geresh is on by default - it isnt guaranteed)
#!Y = jewish year 4 digits (5778)



class TestStringMethods(unittest.TestCase):

    def test_1(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("####"), '##')

    def test_2(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("##h##"), '#h#')

    def test_3(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("#a #A #b #B"), 'ראשון Sunday סיון Sivan')

    def test_4(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("#c #d #D #e #E"), 'א׳ 24 24 כ״ד כד')

    def test_5(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("#m #M #y #Y"), '03 3 תשע״ז 5777')

    def test_6(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("#h ###"), "#h ##")

    def test_7(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("%%v % %v %%% "), datetime(2017, 6,18).strftime('%%v % %v %%% '))

    def test_8(self):
        self.assertEqual(JewishDate(datetime(2017, 6,18)).format("hello #v"), "hello #v")

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()