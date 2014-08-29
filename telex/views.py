"""
Views for the telex server.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 7, 2014.
"""
import os
import re
from subprocess import PIPE
from subprocess import Popen

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.threadlocal import get_current_registry

from everest.interfaces import IUserMessageNotifier
from everest.views.postcollection import PostCollectionView


__docformat__ = 'reStructuredText en'
__all__ = ['PostCommandCollectionView',
           ]


class PostCommandCollectionView(PostCollectionView):
    error_line_pat = re.compile('.*error.*', re.I)
    warning_line_pat = re.compile('.*warn.*', re.I)

    def _get_result(self, resource):
        cmd_ent = resource.get_entity()
        # This is where the command is run.
        exc = CommandExecutor(cmd_ent)
        exc.run()
        result = None
        if cmd_ent.exit_code != 0:
            # We attempt to extract warnings from the stderr output so
            # that the user has the option to submit again ignoring the
            # warnings. An output line is considered a warning if it
            # contains a "WARN" marker (case insensitive).
            warnings = []
            has_errors = False
            for line in cmd_ent.error_string:
                if self.error_line_pat.match(line):
                    has_errors = True
                    break
                elif self.warning_line_pat.match(line):
                    warnings.append(line)
            if not has_errors and len(warnings) > 0:
                if self._enable_messaging:
                    # This triggers a 307 response.
                    reg = get_current_registry()
                    msg_notifier = \
                        reg.getUtility(IUserMessageNotifier)
                    msg_notifier.notify(os.linesep.join(warnings))
                else:
                    msg = os.linesep.join(
                            ['The command triggered the following '
                             'warnings"', cmd_ent.error_string])
                    http_exc = HTTPBadRequest(msg)
                    result = self.request.get_response(http_exc)
            elif has_errors:
                msg = 'The command terminated abnormally.%s%s' \
                      'Error output: %s%sStandard output: %s' \
                      % (os.linesep, os.linesep, cmd_ent.error_string,
                         os.linesep, cmd_ent.error_string)
                http_exc = HTTPBadRequest(msg)
                result = self.request.get_response(http_exc)
        if result is None:
            result = PostCollectionView._get_result(self, resource)
        return result


class CommandExecutor(object):
    """
    Wraps the execution of a command.
    """
    def __init__(self, command):
        self.__command = command

    def run(self):
        """
        Runs the command with the parameters passed during initialization.
        """
        cwd = self.__command.command_definition.working_directory
        if cwd is None:
            # We use the path of the executable as default execution path.
            exc = self.__command.command_definition.executable
            cwd = os.path.dirname(exc)
        child = Popen(self.__command.command_string,
                      shell=True,
                      cwd=os.path.expandvars(cwd),
                      env=self.__command.environment,
                      universal_newlines=True, stdout=PIPE, stderr=PIPE)
        output_string, error_string = child.communicate()
        self.__command.output_string = output_string
        self.__command.error_string = error_string
        self.__command.exit_code = child.returncode
