"""
Resources for the telex server.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 7, 2014.
"""
from datetime import datetime

from everest.resources.base import Member
from everest.resources.descriptors import collection_attribute
from everest.resources.descriptors import member_attribute
from everest.resources.descriptors import terminal_attribute
from telex.interfaces import ICommandDefinition
from telex.interfaces import IParameter
from telex.interfaces import IParameterDefinition
from telex.interfaces import IParameterOption
from telex.interfaces import IRestCommandDefinition
from telex.interfaces import IShellCommandDefinition


__docformat__ = 'reStructuredText en'
__all__ = []


class CommandDefinitionMember(Member):
    relation = 'http://telex.org/relations/command-definition'
    title = 'Command Definition'
    name = terminal_attribute(str, 'name')
    label = terminal_attribute(str, 'label')
    submitter = terminal_attribute(str, 'submitter')
    category = terminal_attribute(str, 'category')
    description = terminal_attribute(str, 'description')
    parameter_definitions = collection_attribute(IParameterDefinition,
                                                 'parameter_definitions')


class ShellCommandDefinitionMember(CommandDefinitionMember):
    relation = 'http://telex.org/relations/shell-command-definition'
    title = 'Shell Command Definition'
    executable = terminal_attribute(str, 'executable')
    working_directory = terminal_attribute(str, 'working_directory')


class RestCommandDefinitionMember(CommandDefinitionMember):
    relation = 'http://telex.org/relations/rest-command-definition'
    title = 'REST Command Definition'
    request_content_type = terminal_attribute(str, 'request_content_type')
    response_content_type = terminal_attribute(str, 'response_content_type')
    url = terminal_attribute(str, 'url')
    operation = terminal_attribute(str, 'operation')


class ParameterDefinitionMember(Member):
    relation = 'http://telex.org/relations/parameter-definition'
    title = 'Parameter Definition'
    name = terminal_attribute(str, 'name')
    label = terminal_attribute(str, 'label')
    description = terminal_attribute(str, 'description')
    command_definition = member_attribute(ICommandDefinition,
                                          'command_definition')
    value_type = terminal_attribute(str, 'value_type')
    parameter_options = collection_attribute(IParameterOption,
                                             'parameter_options')


class ParameterOptionMember(Member):
    relation = 'http://telex.org/relations/parameter-option'
    name = terminal_attribute(str, 'name')
    value = terminal_attribute(str, 'value')


class CommandMember(Member):
    relation = 'http://telex.org/relations/command'
    title = 'Command'
    submitter = terminal_attribute(str, 'submitter')
    timestamp = terminal_attribute(datetime, 'timestamp')
    parameters = collection_attribute(IParameter, 'parameters')


class ShellCommandMember(CommandMember):
    relation = 'http://telex.org/relations/shell-command'
    title = 'Shell Command'
    command_definition = member_attribute(IShellCommandDefinition,
                                          'command_definition')
    output_string = terminal_attribute(str, 'output_string')
    error_string = terminal_attribute(str, 'error_string')
    exit_code = terminal_attribute(int, 'exit_code')


class RestCommandMember(CommandMember):
    relation = 'http://telex.org/relations/rest-command'
    title = 'REST Command'
    command_definition = member_attribute(IRestCommandDefinition,
                                          'command_definition')
    response_status_code = terminal_attribute(int, 'response_status_code')
    response_headers = terminal_attribute(dict, 'response_headers')
    response_body = terminal_attribute(str, 'response_body')

class ParameterMember(Member):
    relation = 'http://telex.org/relations/parameter'
    title = 'Parameter'
    parameter_definition = member_attribute(IParameterDefinition,
                                            'parameter_definition')
    value = terminal_attribute(str, 'value')
