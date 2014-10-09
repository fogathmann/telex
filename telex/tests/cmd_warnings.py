"""
This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 9, 2014.
"""
import os
import sys
from telex.tests.messages import INFO_MSG
from telex.tests.messages import WARNING_MSG


__docformat__ = 'reStructuredText en'
__all__ = []


log_msgs = [INFO_MSG,
            WARNING_MSG,
            ''
            ]

sys.stderr.write(os.linesep.join(log_msgs))
sys.exit(1)