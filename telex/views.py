"""
Views for the telex server.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 7, 2014.
"""
import os
import re

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import status_map
from pyramid.threadlocal import get_current_registry
from requests.exceptions import ConnectionError

from everest.interfaces import IUserMessageNotifier
from everest.views.postcollection import PostCollectionView
from pyramid.httpexceptions import HTTPInternalServerError


__docformat__ = 'reStructuredText en'
__all__ = ['PostRestCommandCollectionView',
           'PostShellCommandCollectionView',
           ]


class PostShellCommandCollectionView(PostCollectionView):
    error_line_pat = re.compile('.* error .*', re.I)
    warning_line_pat = re.compile('.* warn .*', re.I)

    def _get_result(self, resource):
        cmd_ent = resource.get_entity()
        # This is where the command is run.
        cmd_ent.run()
        result = None
        if cmd_ent.exit_code != 0:
            # We attempt to extract error and warning messages from the
            # stderr output. If only warnings were encountered, the user has
            # the option to submit again ignoring the warnings.
            # An output line is considered an error if it contains a
            # " ERROR " marker and a warning if it contains a " WARN " marker
            # (both case insensitive).
            errors = []
            warnings = []
            for line in cmd_ent.error_string.split(os.linesep):
                if self.error_line_pat.match(line):
                    errors.append(line)
                    break
                elif self.warning_line_pat.match(line):
                    warnings.append(line)
            if len(errors) == 0 and len(warnings) > 0:
                if self._enable_messaging:
                    # This triggers a 307 response.
                    reg = get_current_registry()
                    msg_notifier = \
                        reg.getUtility(IUserMessageNotifier)
                    msg_notifier.notify(os.linesep.join(warnings))
                else:
                    msg = os.linesep.join(
                            ['The command triggered the following '
                             'warnings:',
                             cmd_ent.error_string])
                    http_exc = HTTPBadRequest(msg)
                    result = self.request.get_response(http_exc)
            else:
                err_msg = len(errors) == 0 and cmd_ent.error_string \
                          or os.linesep.join(errors)
                msg = os.linesep.join(
                            ['The command terminated abnormally.',
                             'Error output:',
                             err_msg,
                             'Standard output:',
                             cmd_ent.output_string])
                http_exc = HTTPBadRequest(msg)
                result = self.request.get_response(http_exc)
        if result is None:
            result = PostCollectionView._get_result(self, resource)
        return result


class PostRestCommandCollectionView(PostCollectionView):

    def _get_result(self, resource):
        cmd_ent = resource.get_entity()
        # This is where the command is run.
        try:
            cmd_ent.run()
        except ConnectionError, exc:
            # The REST service was unavailable (connection refused). The best
            # thing we can do is to report this as an internal server error on
            # the part of the telex server.
            msg = 'Could  not connect to REST service.' \
                  '\nException details: ' + str(exc)
            result = self.request.get_response(HTTPInternalServerError(msg))
        else:
            if cmd_ent.response_status_code == HTTPUnauthorized.code:
                result = self.request.get_response(HTTPUnauthorized())
                result.headers.update(cmd_ent.response.headers)
            elif cmd_ent.response_status_code != HTTPCreated.code:
                http_exc_cls = status_map[cmd_ent.response_status_code]
                message = "Expected HTTP 201 Created, got HTTP %s %s." \
                          % (http_exc_cls.code, http_exc_cls.title)
                http_exc = HTTPBadRequest(message)
                result = self.request.get_response(http_exc)
            else:
                result = PostCollectionView._get_result(self, resource)
        return result