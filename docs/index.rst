Python Oneliner
---------------

This module improves Python's usefulness as a tool for writing shell
one-liners. A brief usage example:

.. code-block:: bash

    # show line numbers
    python -m oneliner -ne '"%5d: %s" % (NR, _)' < input.txt

    # convert unix timestamp to something more human readable
    date +%s | pyl -j ' => ' -line '_, datetime.datetime.fromtimestamp(int(_))'
    # 1355256353 => 2012-12-11 22:05:53

    # triple space a file
    pyl -ne 'line + "\n"*2' < input.txt

    # double space only non-blank lines:
    pyl -ne '_ if re.match("^$", _) else _+"\n"' input.txt

Why?
----

Python is a wonderful general purpose scripting language with a great breadth of
excellent libraries. While the simplicity of its syntax is often cited as a
major strong point, I believe that the negative attitude towards any kind of
*syntax magic* has prevented Python from becoming a useful tool for writing
shell one-liners. When stacked against the likes of Ruby and Perl, Python is
ill-equipped to be a part of a shell pipeline. Writing one-liners is possible,
but their verbosity makes them impractical. This may be attributed to the
following factors::

1) Lack of a *read-print-loop* command line option. Ruby and Perl
   provide the ``-n`` and ``-p`` switches that makes them assume the
   following loop around code::

      for line in sys.stdin:
          <code>
          if '-p' in options:
              sys.stdout.write(line)

2) No *syntax magic* and no *special variables*. Ruby and Perl provide
   a multitude of cryptic, yet useful variables such as::

      $_   last input line
      $.   current input line number
      $~   the match object returned by the last successful pattern match
      $&   the string matched by last successful pattern match
      $3   the string matched by the 3rd group of the last successful pattern match
      $*   sys.argv
      $>   sys.stdout (default output file)
      $<   sys.stdint (default input file)
      $;   input field separator (default value to str.split())
      $/   record separator (os.linesep)
      $$   os.getpid()

   Please refer to English.rb_ and English.pm_ for more information.

3) Lack of a flexible command line import mechanism. For example, Perl
   has the ``-M`` options::

     perl -MDigest::MD5=md5_hex  => from Digest::MD5 import md5_hex
     perl -MDigest::MD5          => import Digest::MD5

   While the CPython interpreter has the ``-m`` switch, it is not
   suitable for the task at hand. For example, the following one-liner
   will run `random's`_ test suite, instead of printing a random
   number::

     python -m random -c "print(random.randint(10))"

All these points add up to the verbosity of Python one-liners. The
following example demonstrates this:

.. code-block:: bash

    # convert a date to a unix timestamp (using strptime)
    ruby -rdate -pe '$_=Date.strptime($_, "%Y-%m-%d").strftime("%s")'
    perl -MTime::Piece -pe '$_=Time::Piece->strptime($_, "%Y-%m-%d\n")->epoch()'
    python -c 'import sys,datetime; [sys.stdout.write(datetime.datetime.strptime("%Y-%m-%d", i).strftime("%s") for i in sys.stdin]'

But why would anyone want to write one-liners in Python, given these
shortcomings and the available alternatives? I believe that when doing
interactive work on the shell, the first solution that comes to mind
is usually good enough. If that solution is a Python one, why not use
it?


How?
----

Python comes with all the building blocks for implementing a practical
method of writing one-liners. This module tries to address the issues
outlined above. The command line interface is kept as close as that of
Ruby and Perl as reasonable.

1) To help with the processing of input and output, *oneliner*
   provides the the ``-n``, ``-p`` and ``-l`` command line switches.

   * ``-n``: assume the following loop around expressions or
     statements (the distinction will be clarified later)::

       for line in sys.stdin:
           ...

   * ``-p``: like ``-n``, but write the value of ``line`` to stdout at
     the end of each iteration::

       for line in sys.stdin:
           ...
           sys.stdout.write(line)

   * ``-l``: automatic line-ending processing. Roughly equivalent to::

       for line in sys.stdin:
           line = line.strip(os.linesep)
           ...
           sys.stdout.write(line)
           sys.stdout.write(os.linesep)

2) Makes the following variables available in the local namespace of
   each one-liner:

   * ``line``, ``L``, ``_``: The current input line. Unless the ``-l``
     switch is given, the line separatator will be a part of this
     string.

   * ``words``, ``W``: Corresponds to the value of
     ``re.split(delimiter, line)`` where delimiter is the value of the
     ``-d`` option. Defaults to ``\s+``.

     The ``words`` list will return an empty string instead of
     throwing an ``IndexError`` when a non-existent item is
     referenced. This behavior is similar to that of arrays in Ruby
     and field variables in Awk.

   * ``NR``: Current input line number.

   * ``FN``: Current input file name. If oneliner is processing input
     from stdin ``FN`` will be equal to ``<stdin>``, otherwise it
     corresponds to the current input file given on the command
     line. For example::

       echo example | python -m oneliner -ne '"%s:%s\t %s" % (FN, NR, L)'
       => <stdin>:1     example

       python -m oneliner -ne '"%s:%s\t %s" % (FN, NR, L)' example.txt
       => example1.txt:1     line 1

3) Provide the ``-m`` and ``-M`` options and a mini-language for
   specifying imports. This is best illustrated by an example::

    -m os,sys,re,pickle       => import os, sys, re, pickle
    -m os -m sys -m re        => import os, sys, re
    -m os sys re pickle       => import os, sys, re, pickle
    -m os.path.[*]            => from os.path import *
    -m os.path.[join,exists]  => from os.path import join, exists
    -m subprocess=sub         => import subprocess as sub
    -m datetime.[datetime=dt] => from datetime import datetime as dt
    -M os.path                => from os.path import *


Installing
----------

The latest stable version of *python-oneliner* is available on pypi
and may be installed with pip.

.. code-block:: bash

    $ pip install oneliner  # latest stable version

Alternatively, you may simply put the `oneline.py`_ file anywhere in
your load path.


Todo
----

* Support one-liners that don't deal with input/output only. If ``-n``
  or ``-p`` are not given, *python-oneliner* should behave mostly like
  ``python -c`` does.

* Persistent variables in statement one-liners.

* The result of an expression one-liner is always written to stdout
  (even if ``-n``).

* Define the behaviour of multiple expression/statements specified on
  the command line.

* Some means of emulating ``BEGIN`` and ``END`` (perhaps a ``-b`` and
  ``-d`` flag?)

* Add more examples.


Similar Projects
----------------

* Pyp_

* Pyle_

* Funcpy_

* Red_

* Pyfil_

License
-------

*Python-oneliner* is released under the terms of the `Revised BSD License`_.


.. _English.rb: https://github.com/ruby/ruby/blob/trunk/lib/English.rb
.. _English.pm: http://cpansearch.perl.org/src/GBARR/perl5.005_03/lib/English.pm
.. _random's:   http://hg.python.org/cpython/file/16b1fde2275c/Lib/random.py#l728
.. _oneline.py: https://raw.githubusercontent.com/gvalkov/python-oneliner/master/oneliner.py
.. _Pyp:        http://code.google.com/p/pyp/
.. _Pyle:       https://github.com/aljungberg/pyle
.. _Funcpy:     http://www.pixelbeat.org/scripts/funcpy
.. _Red:        https://bitbucket.org/johannestaas/red
.. _Pyfil:      https://github.com/ninjaaron/pyfil
.. _`Revised BSD License`: https://raw.github.com/gvalkov/python-oneliner/master/LICENSE
