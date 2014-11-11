"""

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Sep 26, 2014.
"""
import datetime
import os
import sys

from pyramid.httpexceptions import HTTPCreated
import pytest
from pytz import timezone
import requests

from everest.mime import JsonMime
from everest.resources.utils import get_root_collection
from everest.rfc3339 import rfc3339
from telex.constants import VALUE_TYPES
from telex.entities import Parameter
from telex.entities import RestCommand
from telex.entities import RestCommandDefinition
from telex.entities import ShellCommandDefinition
from telex.interfaces import IRestCommand
from telex.interfaces import IShellCommandDefinition


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
def shell_cmd_def_echo(submitter): # pylint:disable=W0621
    # FIXME: Implicitly depends on either app_creator or resource_repo
    #        fixture.
    cd = ShellCommandDefinition('echo',
                                'Echo command.',
                                submitter,
                                '%s %s' % (sys.executable, SCRIPT),
                                description='Simple command echoing input to '
                                            'stdout.',
                                working_directory=os.path.dirname(__file__))
    pd = cd.add_parameter_definition('text', 'Text', VALUE_TYPES.STRING,
                                     description='Text to echo.')
    pd.add_parameter_option('is_mandatory', True)
    cd_coll = get_root_collection(IShellCommandDefinition)
    return cd_coll.create_member(cd)


@pytest.fixture
def shell_cmd_def_runner(submitter): # pylint:disable=W0621
    cd = ShellCommandDefinition('runner',
                                'Script runner.',
                                submitter,
                                '%s' % sys.executable,
                                description='Simple command running script.',
                                working_directory=os.path.dirname(__file__))
    pd = cd.add_parameter_definition('script', 'Script', VALUE_TYPES.STRING,
                                     description='Script to run.')
    pd.add_parameter_option('is_mandatory', True)
    cd_coll = get_root_collection(IShellCommandDefinition)
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


class MockRequests(object):
    def __init__(self, app):
        self.__app = app

    def __call__(self, operation, url, params=None, headers=None):
        cnt_tpe = headers.pop('content-type', None)
        op_method = getattr(self.__app, operation.lower())
        return op_method(url, params=params, content_type=cnt_tpe,
                         status=HTTPCreated.code)


@pytest.fixture
def app_mocked_request(app_creator_with_request, monkeypatch):
    """
    This redirects the REST operations that are normally carried out through
    the requests.request function to appropriate calls to our test app.
    """
    monkeypatch.setattr(requests, 'request',
                        MockRequests(app_creator_with_request))
    return app_creator_with_request


@pytest.fixture
def rest_cmd(submitter): # pylint:disable=W0621
    cmd_def = RestCommandDefinition('post_echo',
                                    'POST a shell command definition.',
                                    submitter,
                                    '/shell-command-definitions',
                                    JsonMime.mime_type_string
                                    )
    pd1 = cmd_def.add_parameter_definition('name', 'Command name',
                                           VALUE_TYPES.STRING,
                                           description='Name of the command.')
    pd1.add_parameter_option('is_mandatory', True)
    pd2 = cmd_def.add_parameter_definition('label', 'Command label',
                                           VALUE_TYPES.STRING,
                                           description='Label of the '
                                                       'command.')
    pd2.add_parameter_option('is_mandatory', True)
    pd3 = cmd_def.add_parameter_definition('submitter',
                                           'Command definition submitter',
                                           VALUE_TYPES.STRING,
                                           description='Name of the user '
                                                       'submitting the '
                                                       'command definition.')
    pd3.add_parameter_option('is_mandatory', True)
    pd4 = cmd_def.add_parameter_definition('executable',
                                           'Command definition executable',
                                           VALUE_TYPES.STRING,
                                           description='Executable for the '
                                                       'command definition.')
    pd4.add_parameter_option('is_mandatory', True)
    parameters = [Parameter(pd1, 'echo'),
                  Parameter(pd2, 'Echo'),
                  Parameter(pd3, submitter),
                  Parameter(pd4, 'echo')]
    cmd = RestCommand(cmd_def,
                      submitter,
                      parameters,
                      content_type=JsonMime.mime_type_string)
    cmd_coll = get_root_collection(IRestCommand)
    return cmd_coll.create_member(cmd)
