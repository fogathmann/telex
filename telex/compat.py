"""
This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 9, 2014.
"""

__docformat__ = 'reStructuredText en'
__all__ = ['quote',
           ]

from pyramid.compat import PY3


if PY3:
    import shlex
    quote = shlex.quote # pylint: disable=E1101
else:
    # From the pipes module.
    import string # pylint: disable=W0402
    _safechars = frozenset(string.ascii_letters + string.digits + '@%_-+=:,./')
    def quote(arg):
        """Return a shell-escaped version of the file string."""
        for c in arg:
            if c not in _safechars:
                break
        else:
            if not arg:
                return "''"
            return arg
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + arg.replace("'", "'\"'\"'") + "'"
