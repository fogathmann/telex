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


__docformat__ = 'reStructuredText en'
__all__ = []


class CommandDefinitionMember(Member):
    relation = 'http://telex.org/relations/command-definition'
    title = 'Command Definition'
    name = terminal_attribute(str, 'name')
    label = terminal_attribute(str, 'label')
    executable = terminal_attribute(str, 'executable')
    submitter = terminal_attribute(str, 'submitter')
    category = terminal_attribute(str, 'category')
    description = terminal_attribute(str, 'description')
    working_directory = terminal_attribute(str, 'working_directory')
    parameter_definitions = collection_attribute(IParameterDefinition,
                                                 'parameter_definitions')


class ParameterDefinitionMember(Member):
    relation = 'http://telex.org/relations/parameter-definition'
    title = 'Parameter Definition'
    name = terminal_attribute(str, 'name')
    label = terminal_attribute(str, 'label')
    description = terminal_attribute(str, 'description')
    command_definition = member_attribute(ICommandDefinition,
                                          'command_definition')
    value_type = terminal_attribute(str, 'value_type')
    default_value = terminal_attribute(str, 'default_value')
    is_mandatory = terminal_attribute(bool, 'is_mandatory')


class CommandMember(Member):
    relation = 'http://telex.org/relations/command'
    title = 'Command'
    submitter = terminal_attribute(str, 'submitter')
    timestamp = terminal_attribute(datetime, 'timestamp')
    command_definition = member_attribute(ICommandDefinition,
                                          'command_definition')
    parameters = collection_attribute(IParameter, 'parameters')
    output_string = terminal_attribute(str, 'output_string')
    error_string = terminal_attribute(str, 'error_string')
    exit_code = terminal_attribute(int, 'exit_code')


class ParameterMember(Member):
    relation = 'http://telex.org/relations/parameter'
    title = 'Parameter'
    parameter_definition = member_attribute(IParameterDefinition,
                                            'parameter_definition')
    value = terminal_attribute(str, 'value')
