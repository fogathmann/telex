"""
Created on Jul 8, 2014.
"""
import datetime
import os
import sys

from pkg_resources import resource_filename # pylint: disable=E0611
from pyramid.httpexceptions import HTTPCreated
from pytz import timezone

from everest.mime import JsonMime
from everest.resources.utils import get_root_collection
from everest.rfc3339 import rfc3339
from telex.entities import CommandDefinition
from telex.interfaces import ICommand
from telex.interfaces import ICommandDefinition


class TestCommands(object):
    package_name = 'telex.tests'
    app_name = 'telex_test'
    ini_file_path = resource_filename('telex.tests', 'test.ini')
    config_file_name = resource_filename('telex.tests', 'configure.zcml')
    post_data_template_path = \
        resource_filename('telex.tests', 'echo_cmd.json.tmpl')
    path = '/commands'

    def test_simple_command(self, app_creator):
        # First, add a test command definition.
        SCRIPT = 'cmd_echo.py'
        cd = CommandDefinition('echo',
                               '%s %s' % (sys.executable, SCRIPT),
                               working_directory=os.path.dirname(__file__))
        cd.add_parameter_definition('text', str,
                                    is_mandatory=True)
        cd_coll = get_root_collection(ICommandDefinition)
        cd_coll.create_member(cd)
        # Now, read the JSON command template and expand.
        with open(self.post_data_template_path, 'rU') as data_tmpl_file:
            data_tmpl = data_tmpl_file.read()
        utc = timezone('UTC')
        TIMESTAMP = datetime.datetime(2012, 8, 29, 16, 20, 0, tzinfo=utc)
        ldt_rpr = rfc3339(TIMESTAMP, use_system_timezone=False)
        TEXT = 'Hello Mars!'
        USER = "telexuser"
        post_data = data_tmpl % dict(app_name=self.app_name,
                                     text=TEXT,
                                     timestamp=ldt_rpr,
                                     user=USER)
        # Perform the POST.
        app_creator.post(self.path,
                         params=post_data,
                         content_type=JsonMime.mime_type_string,
                         status=HTTPCreated.code)
        c_coll = get_root_collection(ICommand)
        cmd_mb = next(iter(c_coll))
        assert cmd_mb.exit_code == 0
        assert cmd_mb.user == USER
        assert cmd_mb.timestamp == TIMESTAMP
        argv = cmd_mb.output_string.strip().split(',')
        assert argv[0] == SCRIPT
        assert argv[1] == TEXT

