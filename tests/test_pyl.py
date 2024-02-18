#!/usr/bin/env python

from pytest import mark
from oneliner import *


def test_module_finder():
    mic = modules_in_code
    assert mic("write(sys.version)") == ["sys"]
    assert mic("abc.write sys.version.none") == ["abc", "sys"]
    assert mic(";sys.stdout.write();") == ["sys"]


def test_module_split():
    pms = parse_modules_split
    assert pms("os,sys,re") == ["os", "sys", "re"]
    assert pms("os, sys, re") == ["os", "sys", "re"]
    assert pms("os,sys, re,") == ["os", "sys", "re"]
    assert pms("os.path,sys,") == ["os.path", "sys"]

    assert pms("os.path.[exists]") == ["os.path.[exists]"]
    assert pms("os.path.[exists,join]") == ["os.path.[exists,join]"]
    assert pms("sys,os.path.[exists]") == ["sys", "os.path.[exists]"]
    assert pms("sys,os.path.[*]") == ["sys", "os.path.[*]"]
    assert pms("sys,os.path.[exists,join],re") == ["sys", "os.path.[exists,join]", "re"]


def test_parse_modules():
    pm = parse_modules
    assert pm("subprocess") == [(("subprocess", ""), [])]
    assert pm("subprocess=sub") == [(("subprocess", "sub"), [])]
    assert pm("sys=s,os=o") == [(("sys", "s"), []), (("os", "o"), [])]

    assert pm("os.path.[exists]") == [(("os.path", ""), [("exists", "")])]
    assert pm("os.path.[exists,join]") == [(("os.path", ""), [("exists", ""), ("join", "")])]
    assert pm("os.path.[exists=e,join=j]") == [(("os.path", ""), [("exists", "e"), ("join", "j")])]
    assert pm("sys,os.path.[*]") == [(("sys", ""), []), (("os.path", ""), [("*", "")])]


def test_import_modules():
    im = lambda x: sorted(import_modules(parse_modules(x)))
    assert im("sys,os,re") == ["os", "re", "sys"]
    assert im("subprocess=sub") == ["sub"]
    assert im("subprocess=sub,sys") == ["sub", "sys"]
    assert im("sys=a,os=b,re=c") == ["a", "b", "c"]

    assert im("os.path.[exists]") == ["exists"]
    assert im("sys=s,os.path.[exists]") == ["exists", "s"]
    assert im("os.path.[exists,join]") == ["exists", "join"]
    assert im("os.path.[exists=e,join=j]") == ["e", "j"]


def test_import_modules_wildcard():
    res = import_modules(parse_modules("os.path.[*]"))
    assert all([i in res for i in ["join", "isdir", "abspath"]])


def test_default_list():
    l = defaultlist([1, 2, 3])
    assert l[0] == 1
    assert l[10] == None

    l = defaultlist([1, 2, 3], default=True)
    assert l[10] == True


def test_functional():
    data, args = "example", ["-ne", "line.upper()"]
    assert run(args, data) == "EXAMPLE"

    data, args = "example", ["-ns", "print(line.upper())"]
    assert run(args, data) == "EXAMPLE\n"

    data = "1355256353"
    args = ["-j", " => ", "-line" "_, datetime.datetime.fromtimestamp(int(_))"]
    assert run(args, data) == "1355256353 => 2012-12-11 21:05:53\n"


# -----------------------------------------------------------------------------
# utility functions
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def stdinstr(s):
    fh = StringIO(s)
    fh.isatty = lambda: False
    return fh


def run(args, data):
    res = StringIO()
    main(args, stdinstr(data), fh_out=res)
    return res.getvalue()
