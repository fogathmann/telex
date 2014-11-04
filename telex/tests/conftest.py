"""

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Sep 26, 2014.
"""
import datetime
import os
import sys

import pytest
from pytz import timezone

from everest.resources.utils import get_root_collection
from everest.rfc3339 import rfc3339
from telex.entities import CommandDefinition
from telex.interfaces import ICommandDefinition
from telex.constants import VALUE_TYPES


__docformat__ = 'reStructuredText en'
__all__ = []


SCRIPT = 'cmd_echo.py'


def read_resource(path):
    with open(path, 'rU') as rc_file:
        return rc_file.read()


@pytest.fixture
def submitter():
    return 'telexmasteruser'


@pytest.fixture
def timestamp():
    utc = timezone('UTC')
    return datetime.datetime(2012, 8, 29, 16, 20, 0, tzinfo=utc)


@pytest.fixture
def cmd_def_echo(submitter): # pylint:disable=W0621
    # FIXME: Implicitly depends on either app_creator or resource_repo
    #        fixture.
    cd = CommandDefinition('echo',
                           'Echo command',
                           '%s %s' % (sys.executable, SCRIPT),
                           submitter,
                           description='Simple command echoing input to '
                                       'stdout.',
                           working_directory=os.path.dirname(__file__))
    pd = cd.add_parameter_definition('text', 'Text', VALUE_TYPES.STRING,
                                     description='Text to echo.')
    pd.add_parameter_option('is_mandatory', True)
    cd_coll = get_root_collection(ICommandDefinition)
    return cd_coll.create_member(cd)


@pytest.fixture
def cmd_def_runner(submitter): # pylint:disable=W0613,W0621
    cd = CommandDefinition('runner',
                           'Script runner.',
                           '%s' % sys.executable,
                           submitter,
                           description='Simple command running a script.',
                           working_directory=os.path.dirname(__file__))
    pd = cd.add_parameter_definition('script', 'Script', VALUE_TYPES.STRING,
                                     description='Script to run.')
    pd.add_parameter_option('is_mandatory', True)
    cd_coll = get_root_collection(ICommandDefinition)
    return cd_coll.create_member(cd)


@pytest.fixture
def cmd_def_data(request):
    path = request.cls.command_definition_data_path
    return read_resource(path)


@pytest.fixture
def prm_def_data(request):
    path = request.cls.parameter_definition_data_path
    return read_resource(path)


@pytest.fixture
def cmd_data_template(request, submitter, timestamp): # pylint:disable=W0621
    tmpl_path = request.cls.command_template_path
    tmpl_data = read_resource(tmpl_path)
    ldt_rpr = rfc3339(timestamp, use_system_timezone=False)
    return tmpl_data % dict(app_name=request.cls.app_name,
                            timestamp=ldt_rpr,
                            submitter=submitter)
