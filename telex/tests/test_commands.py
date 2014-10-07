"""
Created on Jul 8, 2014.
"""
import datetime

from pkg_resources import resource_filename # pylint: disable=E0611
from pyramid.httpexceptions import HTTPCreated
import pytest
from pytz import timezone

from everest.mime import JsonMime
from everest.resources.utils import get_root_collection
from everest.rfc3339 import rfc3339
from telex.interfaces import ICommand


def read_resource(path):
    with open(path, 'rU') as data_tmpl_file:
        return data_tmpl_file.read()


class TestCommands(object):
    package_name = 'telex.tests'
    app_name = 'telex_test'
    ini_file_path = resource_filename('telex.tests', 'test.ini')
    config_file_name = resource_filename('telex.tests', 'configure.zcml')
    command_template_path = \
                    resource_filename('telex.tests', 'echo_cmd.json.tmpl')
    commands_path = '/commands'

    def test_simple_command(self, app_creator, cmd_def_collection):
        utc = timezone('UTC')
        TIMESTAMP = datetime.datetime(2012, 8, 29, 16, 20, 0, tzinfo=utc)
        ldt_rpr = rfc3339(TIMESTAMP, use_system_timezone=False)
        TEXT = 'Hello Mars!'
        SUBMITTER = "telexuser"
        template = read_resource(self.command_template_path)
        post_data = template % dict(app_name=self.app_name,
                                    text=TEXT,
                                    timestamp=ldt_rpr,
                                    submitter=SUBMITTER)
        # Perform the POST.
        app_creator.post(self.commands_path,
                         params=post_data,
                         content_type=JsonMime.mime_type_string,
                         status=HTTPCreated.code)
        c_coll = get_root_collection(ICommand)
        cmd_mb = next(iter(c_coll))
        assert cmd_mb.exit_code == 0
        assert cmd_mb.submitter == SUBMITTER
        assert cmd_mb.timestamp == TIMESTAMP
        argv = cmd_mb.output_string.strip().split(',')
        assert argv[0] == cmd_mb.command_definition.executable.split(' ')[-1]
        assert argv[1] == TEXT
        assert cmd_mb.command_definition == next(iter(cmd_def_collection))


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

    def test_cmddef_then_paramdef(self, app_creator):
        cmd_def_post_data = read_resource(self.command_definition_data_path)
        rsp = app_creator.post(self.command_definitions_path,
                               params=cmd_def_post_data,
                               content_type=JsonMime.mime_type_string,
                               status=HTTPCreated.code)
        assert rsp.body.find('echo') != -1
        prm_def_post_data = read_resource(self.parameter_definition_data_path)
        app_creator.post(self.parameter_definitions_path,
                         params=prm_def_post_data,
                         content_type=JsonMime.mime_type_string,
                         status=HTTPCreated.code)

class TestSequentialPostsMemory(_TestSequentialPosts):
    config_file_name = resource_filename('telex.tests', 'configure.zcml')


@pytest.mark.usefixtures('rdb')
class TestSequenctialPostsRdb(_TestSequentialPosts):
    config_file_name = resource_filename('telex.tests', 'configure_rdb.zcml')
