"""
Created on Jul 8, 2014.
"""
from pkg_resources import resource_filename # pylint: disable=E0611
from pyramid.compat import native_
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPRedirection
import pytest

from everest.mime import JsonMime
from everest.resources.utils import get_root_collection
from telex.interfaces import ICommand
from telex.tests.messages import ERROR_MSG
from telex.tests.messages import INFO_MSG
from telex.tests.messages import WARNING_MSG


TEXT = 'Hello Mars!'

class _TestTelexCommandBase(object):
    package_name = 'telex.tests'
    app_name = 'telex_test'
    ini_file_path = resource_filename('telex.tests', 'test.ini')
    config_file_name = resource_filename('telex.tests', 'configure.zcml')
    commands_path = '/commands'


class TestSimpleCommand(_TestTelexCommandBase):
    command_template_path = \
                    resource_filename('telex.tests', 'echo_cmd.json.tmpl')

    def test_simple_command(self, app_creator, cmd_def_echo,
                            submitter, timestamp, cmd_data_template):
        post_data = cmd_data_template % dict(param=TEXT)
        # Perform the POST.
        app_creator.post(self.commands_path,
                         params=post_data,
                         content_type=JsonMime.mime_type_string,
                         status=HTTPCreated.code)
        c_coll = get_root_collection(ICommand)
        cmd_mb = next(iter(c_coll))
        assert cmd_mb.exit_code == 0
        assert cmd_mb.submitter == submitter
        assert cmd_mb.timestamp == timestamp
        argv = cmd_mb.output_string.strip().split(',')
        assert argv[0] == cmd_mb.command_definition.executable.split(' ')[-1]
        assert argv[1] == TEXT
        assert cmd_mb.command_definition == cmd_def_echo


@pytest.mark.usefixtures('app_creator', 'cmd_def_runner')
class TestCommandOutput(_TestTelexCommandBase):
    command_template_path = \
                    resource_filename('telex.tests', 'runner_cmd.json.tmpl')

    def test_warnings(self, app_creator, cmd_data_template):
        post_data = cmd_data_template % dict(param='cmd_warnings.py')
        # Perform the POST.
        rsp = app_creator.post(self.commands_path,
                               params=post_data,
                               content_type=JsonMime.mime_type_string,
                               status=HTTPRedirection.code)
        assert rsp.headers.get('warning').endswith(WARNING_MSG)
        c_coll = get_root_collection(ICommand)
        cmd_mb = next(iter(c_coll))
        assert cmd_mb.exit_code == 1

    def test_errors(self, app_creator, cmd_data_template):
        post_data = cmd_data_template % dict(param='cmd_errors.py')
        # Perform the POST.
        rsp = app_creator.post(self.commands_path,
                               params=post_data,
                               content_type=JsonMime.mime_type_string,
                               status=HTTPBadRequest.code)
        body = native_(rsp.body)
        assert body.find('The command terminated abnormally.') != -1
        assert body.find(ERROR_MSG) != -1
        assert body.find(INFO_MSG) == -1
        c_coll = get_root_collection(ICommand)
        cmd_mb = next(iter(c_coll))
        assert cmd_mb.exit_code == 1

    def test_errors_and_warnings(self, app_creator, cmd_data_template):
        post_data = cmd_data_template \
                    % dict(param='cmd_errors_and_warnings.py')
        # Perform the POST.
        rsp = app_creator.post(self.commands_path,
                               params=post_data,
                               content_type=JsonMime.mime_type_string,
                               status=HTTPBadRequest.code)
        body = native_(rsp.body)
        assert body.find('The command terminated abnormally.') != -1
        assert body.find(ERROR_MSG) != -1
        assert body.find(INFO_MSG) == -1
        assert body.find(WARNING_MSG) == -1
        c_coll = get_root_collection(ICommand)
        cmd_mb = next(iter(c_coll))
        assert cmd_mb.exit_code == 1


class _TestSequentialPosts(object):
    package_name = 'telex.tests'
    app_name = 'telex_test'
    ini_file_path = resource_filename('telex.tests', 'test.ini')
    command_definition_data_path = \
                    resource_filename('telex.tests', 'echo_cmd_def.json.tmpl')
    parameter_definition_data_path = \
                    resource_filename('telex.tests', 'echo_prm_def.json.tmpl')
    command_definitions_path = '/command-definitions'
    parameter_definitions_path = command_definitions_path \
                                 + '/echo/parameter-definitions'

    def test_cmddef_then_paramdef(self, app_creator, cmd_def_data,
                                  prm_def_data):
        rsp = app_creator.post(self.command_definitions_path,
                               params=cmd_def_data,
                               content_type=JsonMime.mime_type_string,
                               status=HTTPCreated.code)
        assert rsp.body.find('echo') != -1
        app_creator.post(self.parameter_definitions_path,
                         params=prm_def_data,
                         content_type=JsonMime.mime_type_string,
                         status=HTTPCreated.code)


class TestSequentialPostsMemory(_TestSequentialPosts):
    config_file_name = resource_filename('telex.tests', 'configure.zcml')


@pytest.mark.usefixtures('rdb')
class TestSequenctialPostsRdb(_TestSequentialPosts):
    config_file_name = resource_filename('telex.tests', 'configure_rdb.zcml')
