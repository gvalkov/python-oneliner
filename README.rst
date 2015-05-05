*oneliner*
----------

This module tries to improve Python's usefulness as a tool for writing
shell one-liners.

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

Documentation:
    http://python-oneliner.readthedocs.org/en/latest/

Development:
    https://github.com/gvalkov/python-oneliner

Package:
    http://pypi.python.org/pypi/oneliner
