#!/usr/bin/env python

from __future__ import print_function

import os
import re
import sys
import argparse

from sys import stderr, stdout, stdin


usage = '''\
Usage: {} [flags] [-m modules] [-e <expr>] [-s <stmt>] <path> [<path>...]

Options:
  -h       show this help message and exit
  -v       show version and exit
  -n       run statement or expression for each line of input
  -p       like -n, but print value of 'line' every input cycle
  -d       field delimiter regex (default: '\s+')
  -i       attempt to automatically import module names
  -j       join tuples or lists before printing
  -l       chomp newlines from input
  -m mod   modules to import (see Importing Modules)
  -e expr  python expression (see Execution Model)
  -s stmt  python statement (see Execution Model)
  --debug  enable debugging

Execution Model:
  When given the '-n' or '-p' flags, oneliner evaluates expressions or
  statements for each line of stdin. The local namespace of your code
  includes the following variables:

    line L _ => current input line
    words W  => re.split(delimiter, line) (see '-d' option)
    NR       => current input line number
    FN       => current input file name (or stdin)

  If an expression is used, its return value is written to stdout:

    echo example | pyl -ne 'line.upper()' => EXAMPLE

  Statements must take care of output processing. If the '-p' flag is
  given, the value of the 'line' variable is written to stdout at the
  end of each iteration.

    echo example | pyl -ns 'print(line.upper())' => EXAMPLE
    echo example | pyl -ps 'line=line.upper()' => EXAMPLE

  The '-e' and '-s' options cannot be mixed.

  If the '-j' flag is set, tuples and lists returned by expressions
  will be joined by a single space. The delimiter can be configured by
  passing a value to '-j'.

Importing Modules:
  The '-m' option imports modules into the global namespace of each
  evaluated expression or statement. The '-m' option can be specified
  multiple times. Examples:

    -m os,sys,re,pickle => import os, sys, re, pickle
    -m os -m sys -m re  => import os, sys, re
    -m os sys re pickle => import os, sys, re, pickle
    -m os.path.[*]      => from os.path import *
    -m subprocess=sub   => import subprocess as sub
    -m os.path.[join,exists]  => from os.path import join, exists
    -m datetime.[datetime=dt] => from datetime import datetime as dt

  The os, sys and re modules are included by default.

  The '-i' flag will attempt to import all top-level module names
  found in an expression or statement. In the following example the
  'time' module will be imported automatically:

    yes | pyl -j -line '(time.time(), line)'

'''.format('pyl' if 'pyl' in sys.argv[0] else 'python -m oneliner')

# modules that will be made available to commands by default
provided_modules = ('os', 're', 'sys',)


class defaultlist(list):
    '''A list that returns a default value on IndexErrors.'''
    def __init__(self, iterable, default=None):
        list.__init__(self, iterable)
        self._default = default

    def __getitem__(self, index):
        try:
            return list.__getitem__(self, index)
        except IndexError:
            return self._default


def parse_args(argv):
    '''Parse arguments and do a basic sanity check.'''
    parser = argparse.ArgumentParser(add_help=False)
    addarg = parser.add_argument

    addarg('-h', '--help', action='store_true')
    addarg('-v', '--version', action='version', version='%(prog)s version 0.1.0')
    addarg('-n', action='store_true', dest='readloop')
    addarg('-p', action='store_true', dest='printloop')
    addarg('-l', action='store_true', dest='chomp')
    addarg('-i', action='store_true', dest='autoimports')
    addarg('-d', default=r'\s+', dest='fssep')
    addarg('-j', nargs='?', dest='joinsep', default='', const=' ')
    addarg('-m', nargs='*', dest='mods', default=[])
    addarg('-e', nargs=1, dest='expr', default=[])
    addarg('-s', nargs=1, dest='stmt', default=[])
    addarg('--debug', action='store_true')
    addarg('inputs',  nargs='*', type=argparse.FileType('r'))

    parser.print_usage = lambda file: print(usage, file=file)
    opts = parser.parse_args(argv)

    if opts.help:
        print(usage, file=stderr)
        sys.exit(1)

    try:
        err = Exception
        if stdin.isatty() and not opts.inputs:
            raise err('no input files or input on stdin')
        if not stdin.isatty() and opts.inputs:
            raise err('multiple input sources (stdin and command line)')
        if opts.expr and opts.stmt:
            raise err('cannot use expression and statement oneliners at the same time')
        if not opts.expr and not opts.stmt:
            raise err('error: no expression or statement specified')
    except Exception as e:
        print(usage, file=stderr)
        print('error: %s' % e.message)
        sys.exit(1)

    return opts


def parse_modules_split(line):
    '''Split a comma separated list of module names, excluding commas
       between brackets. Example:

         'sys,os,re' => ['sys', 'os', 're']
         'sys,os.path.[exists,join],re' => ['sys', 'os.path.[exists,join]', 're']
    '''
    if '[' not in line:
        # os,sys,re -> ['os', 'sys', 're']
        mods = [i for i in re.split(r'[,\s]', line) if i]
    else:
        # sys,os.path.[join,exists] -> ['sys', 'os.path.[join,exists]']
        mods = []

        # positions of matching '[.*]' pairs within line
        # '0[23]5[78] -> [1,2,3,4,6,7,8,9]
        brackets = re.finditer(r'\[[^\]]*\]', line)
        brackets = [range(*m.span()) for m in brackets]
        brackets = [j for i in brackets for j in i]

        commas = list(re.finditer(r',', line))

        line = list(line)
        for m in commas:
            pos = m.start()
            if pos not in brackets:
                line[pos] = '$'

        mods = ''.join(line).split('$')

    return mods


def parse_modules(line):
    '''Parse shorthand import statements. Example:

         'os.path.[exists=e,join=j]'
         => [(('os.path', ''), [('exists', 'e'), ('join', 'j')])]

         'os.path.[exists]'
         => [(('os.path', ""), [('exists', '')])]

         'subprocess=sub', 'sys'
         => [(('subprocess', 'sub'), []), (('sys', ''), [])]
    '''
    mods = parse_modules_split(line)
    imports = []

    for mod in mods:
        # 'os.path.[exists,join]' -> ['os.path', ['exists', 'join']]
        if '[' in mod:
            mod, names, _ = re.split('\.?\[(.*)\]', mod)
            names = names.split(',')
        else:
            mod, names = mod, []

        name_local = []
        for name in names:
            # 'datetime=dt' -> ['datetime', '=', 'dt']
            name, _, local = name.partition('=')
            name_local.append((name, local))

        mod, _, local = mod.partition('=')

        imports.append(((mod, local), name_local))

    return imports


def safe_import(*args, **kw):
    try:
        return __import__(*args, **kw)
    except ImportError:
        pass


def import_modules(imports):
    '''Import the results of parse_modules().'''
    ctx = {}

    for module, names in imports:
        module, module_local = module
        module_local = module_local if module_local else module

        g, l = {}, {}

        if not names:
            ctx[module_local] = safe_import(module, g, l, [], -1)
            continue

        tnames = [i[0] for i in names]

        if '*' not in tnames:
            tmp = safe_import(module, g, l, tnames, -1)
            for name, name_local in names:
                name_local = name_local if name_local else name
                ctx[name_local] = getattr(tmp, name)
        else:
            tmp = safe_import(module, g, l, ['*'], -1)
            ctx.update(tmp.__dict__)

    return ctx


def parse_import_modules(mods):
    ctx = {}
    for line in mods:
        imports = parse_modules(line)
        ctx.update(import_modules(imports))

    return ctx


def modules_in_code(expr):
    '''Get module names used in an expression or statement.'''
    return re.findall(r'(?<!\.)(\b\w+)\.', expr)


def main(argv=sys.argv[1:], fh_in=stdin, fh_out=stdout):
    opts = parse_args(argv)

    if isinstance(fh_in, str):
        from StringIO import StringIO
        fh_in = StringIO(fh_in)

    if fh_in.isatty() and opts.inputs:
        from fileinput import FileInput
        fh_in = FileInput(i.name for i in opts.inputs)

    stmt, expr, mods = opts.stmt, opts.expr, opts.mods
    _main(expr, stmt, mods, opts, fh_in, fh_out)


def _main(expr, stmt, mods, opts, fh_in, fh_out):
    if opts.autoimports:
        from itertools import chain
        for i in chain(expr, stmt):
            if i: mods.extend(modules_in_code(i))

    mods.extend(provided_modules)
    ctx = parse_import_modules(mods)

    try:
        code_expr = [compile(i, '<expr>', 'eval') for i in expr if i]
        code_stmt = [compile(i, '<stmt>', 'exec') for i in stmt if i]
    except SyntaxError as e:
        msg = 'syntax error in: %s'
        print(msg % e.text.strip(), file=stderr)
        sys.exit(1)

    if opts.printloop or opts.readloop:
        nloop(code_expr, code_stmt, opts, ctx, fh_in, fh_out)


def nloop(code_expr, code_stmt, opts, ctx, fh_in, fh_out):
    re_delim = re.compile(opts.fssep)
    joinsep = opts.joinsep
    hasfn = hasattr(fh_in, 'filename')

    if code_expr:
        code_objects = code_expr
        isexpr = True
    else:
        code_objects = code_stmt
        isexpr = False

    for nr, line in enumerate(fh_in):
        line = line.strip(os.linesep) if opts.chomp else line
        words = [i.strip() for i in re_delim.split(line) if i]
        words = defaultlist(words, default='')

        eval_globals = ctx.copy()
        eval_locals = {
                'line': line,
                'words': words,
                'NR': nr + 1,
                'L': line,
                '_': line,
                'W': words,
                'FN': fh_in.filename() if hasfn else '<stdin>',
                }

        for i in code_objects:
            res = eval(i, eval_globals, eval_locals)

            if res and isexpr:
                if joinsep and isinstance(res, (tuple, list)):
                    res = joinsep.join(map(str, res))
                eval_locals['line'] = res
                fh_out.write(str(res))
                if opts.chomp:
                    fh_out.write(os.linesep)

        if opts.printloop:
            res = str(eval_locals['line'])
            fh_out.write(res)


if __name__ == '__main__':
    main(sys.argv[1:], stdin, stdout)
