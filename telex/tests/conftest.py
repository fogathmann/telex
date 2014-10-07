"""

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Sep 26, 2014.
"""
import os
import sys

import pytest

from everest.resources.utils import get_root_collection
from telex.entities import CommandDefinition
from telex.interfaces import ICommandDefinition


__docformat__ = 'reStructuredText en'
__all__ = []


SCRIPT = 'cmd_echo.py'
SUBMITTER = 'telexmasteruser'


@pytest.fixture
def cmd_def_collection():
    cd = CommandDefinition('echo',
                           'Echo command',
                           '%s %s' % (sys.executable, SCRIPT),
                           SUBMITTER,
                           description='Simple command echoing input to '
                                       'stdout.',
                           working_directory=os.path.dirname(__file__))
    cd.add_parameter_definition('text', 'Text', str,
                                description='Text to echo.',
                                is_mandatory=True)
    cd_coll = get_root_collection(ICommandDefinition)
    cd_coll.create_member(cd)
    return cd_coll



