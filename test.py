from unittest import TestCase, main as unitmain
from oneliner import *


class TestModuleFinder(TestCase):
    tests = {
        'write(sys.version)'         : ['sys'],
        'abc.write sys.version.none' : ['abc', 'sys'],
        ';sys.stdout.write();'       : ['sys'],
        }

    def test(self):
        for code, res in self.tests.items():
            mods = modules_in_code(code)
            self.assertEqual(mods, res)


class TestModuleParser(TestCase):
    def dotests(self, tests, cb):
        for line, res in tests.items():
            mods = cb(line)
            self.assertEqual(mods, res)

    def test_simple_split(self):
        tests = {
            'os,sys,re'    : ['os', 'sys', 're'],
            'os, sys, re'  : ['os', 'sys', 're'],
            'os,sys, re,'  : ['os', 'sys', 're'],
            'os.path,sys,' : ['os.path', 'sys'],
            }

        self.dotests(tests, parse_modules_split)

    def test_brackets_split(self):
        tests = {
            'os.path.[exists]'     : ['os.path.[exists]'],
            'os.path.[exists,join]': ['os.path.[exists,join]'],
            'sys,os.path.[exists]' : ['sys', 'os.path.[exists]'],
            'sys,os.path.[*]'      : ['sys', 'os.path.[*]'],
            'sys,os.path.[exists,join],re' : ['sys', 'os.path.[exists,join]', 're'],
            }

        self.dotests(tests, parse_modules_split)

    def test_simple_locals(self):
        tests = {
            'subprocess'     : [( ('subprocess', ''), [] )],
            'subprocess=sub' : [( ('subprocess', 'sub'), [] )],
            'sys=s,os=o'     : [( ('sys', 's'), [] ), ( ('os', 'o'), [] )],
            }

        self.dotests(tests, parse_modules)

    def test_brackets(self):
        tests = {
            'os.path.[exists]' :
                [( ('os.path', ""), [('exists', '')])],
            'os.path.[exists,join]':
                [( ('os.path', ""), [('exists', ''), ('join', '')])],
            'os.path.[exists=e,join=j]':
                [( ('os.path', ""), [('exists', 'e'), ('join', 'j')])],
            'sys,os.path.[*]':
                [( ('sys', ''), [] ), ( ('os.path', ''), [('*', '')] )]
            }

        self.dotests(tests, parse_modules)


class TestModuleImport(TestCase):
    def dotests(self, tests, cb):
        for line, expect in tests.items():
            res = cb(parse_modules(line))
            self.assertEqual(sorted(res.keys()), sorted(expect))

    def test_simple(self):
        tests = {
            'sys,os,re' : ['os', 're', 'sys'],
            'subprocess=sub' : ['sub'],
            'subprocess=sub,sys' : ['sub', 'sys'],
            'sys=a,os=b,re=c' : ['a', 'b', 'c'],
            }

        self.dotests(tests, import_modules)

    def test_brackets(self):
        tests = {
            'os.path.[exists]' : ['exists'],
            'sys=s,os.path.[exists]' : ['exists', 's'],
            'os.path.[exists,join]' : ['exists', 'join'],
            'os.path.[exists=e,join=j]' : ['e', 'j'],
            }

        self.dotests(tests, import_modules)

    def test_wildcard(self):
        res = import_modules(parse_modules('os.path.[*]'))
        for i in 'join', 'isdir', 'abspath':
            self.assertTrue(i in res)


if __name__ == '__main__':
    unitmain()
