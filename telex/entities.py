"""
Entities for the telex server.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 7, 2014.
"""
import datetime
import json
import os
from subprocess import PIPE
from subprocess import Popen

from pyramid.threadlocal import get_current_request
from pytz import timezone
import requests

from everest.constants import RequestMethods
from everest.entities.base import Entity
from everest.representers.converters import ConverterRegistry
from telex.compat import quote
from telex.constants import ParameterOptionRegistry
from telex.constants import VALUE_TYPES


__docformat__ = 'reStructuredText en'
__all__ = ['Command',
           'CommandDefinition',
           'Parameter',
           'ParameterDefinition',
           'ParameterOption',
           ]


class CommandDefinition(Entity):
    """
    Command definition.
    """
    #: Name of the command. Needs to be unique.
    name = None
    #: Human-readable, explanatory label.
    label = None
    #: User submitting the command.
    submitter = None
    #: Category this command definition belongs to. Optional.
    category = None
    #: Description of the purpose of this command definition. Optional.
    description = None
    #: List of parameter definitions for this command definition.
    parameter_definitions = None
    #:
    command_definition_type = None

    def __init__(self, name, label, submitter, category=None,
                 description=None, parameter_definitions=None, **kw):
        if type(self) is CommandDefinition:
            raise NotImplementedError('Abstract class.')
        Entity.__init__(self, **kw)
        self.name = name
        self.label = label
        self.submitter = submitter
        self.category = category
        self.description = description
        if parameter_definitions is None:
            parameter_definitions = []
        self.parameter_definitions = parameter_definitions

    @property
    def slug(self):
        return self.name

    def add_parameter_definition(self, name, label, value_type,
                                 description=None):
        init_data = dict(name=name,
                         label=label,
                         value_type=value_type,
                         description=description)
        pd = ParameterDefinition.create_from_data(init_data)
        self.parameter_definitions.append(pd)
        if pd.command_definition is None:
            pd.command_definition = self
        return pd


class ShellCommandDefinition(CommandDefinition):
    #: Executable to run.
    executable = None
    #: Environment variables to set for the command execution. Optional.
    environment = None
    #: Working directory to run the command in. Optional.
    working_directory = None

    def __init__(self, name, label, submitter, executable,
                 environment=None, working_directory=None, **kw):
        CommandDefinition.__init__(self, name, label, submitter, **kw)
        self.command_definition_type = 'SHELL'
        self.executable = executable
        self.environment = environment
        self.working_directory = working_directory


class RestCommandDefinition(CommandDefinition):
    #: URL to compose.
    url = None
    #: MIME content type of the request.
    request_content_type = None
    #: MIME content type of the response.
    response_content_type = None
    #: HTML operation.
    operation = None

    def __init__(self, name, label, submitter, url,
                 request_content_type, response_content_type=None,
                 operation=RequestMethods.POST, **kw):
        CommandDefinition.__init__(self, name, label, submitter, **kw)
        self.command_definition_type = 'REST'
        self.url = url
        self.request_content_type = request_content_type
        if response_content_type is None:
            response_content_type = request_content_type
        self.response_content_type = response_content_type
        self.operation = operation


class ParameterDefinition(Entity):
    """
    Parameter definition within a command definition.
    """
    #: Name of the parameter definition. Needs to be unique within the
    #: referenced command definition.
    name = None
    #: Human-readable, explanatory label.
    label = None
    #: Optional description of the purpose of this parameter.
    description = None
    #: Value type of the parameter.
    value_type = None
    #: Command definition holding this parameter definition.
    command_definition = None
    #: List of parameter options for this parameter definition.
    parameter_options = None
    #: Dictionary mapping parameter option names to their values.
    __po_map = None
    #: Dictionary mapping parameter option types to their Python types.
    __type_map = {VALUE_TYPES.BOOLEAN : bool,
                  VALUE_TYPES.INT : int,
                  VALUE_TYPES.DOUBLE : float,
                  VALUE_TYPES.DATETIME : datetime.datetime,
                  }

    def __init__(self, name, label, command_definition, value_type,
                 description=None, parameter_options=None, **kw):
        Entity.__init__(self, **kw)
        self.name = name
        self.label = label
        self.command_definition = command_definition
        self.value_type = value_type
        self.description = description
        if parameter_options is None:
            parameter_options = []
        self.parameter_options = parameter_options

    @property
    def slug(self):
        """
        Using the `name` attribute as a slug. Note that the name is only
        unique within the scope of a single command definition.
        """
        return self.name
#        return "%s_%s" % (self.command_definition.name, self.name)

    @classmethod
    def create_from_data(cls, data):
        if not 'command_definition' in data:
            data['command_definition'] = None
        if 'parameter_options' in data:
            # Pre-processing. We ignore parameter options with a None value
            # and convert incoming representations to the corresponding
            # Python value.
            value_type = data['value_type']
            pos = []
            opts = ParameterOptionRegistry.get(value_type)
            po_type_map = dict([(opt[0], opt[1]) for opt in opts])
            for po in data['parameter_options']:
                if po.value is None:
                    continue
                py_type = cls.__type_map.get(po_type_map[po.name])
                if not py_type is None:
                    py_value = ConverterRegistry.convert_from_representation(
                                                        po.value,
                                                        py_type)
                    po.value = py_value
                pos.append(po)
            data['parameter_options'] = pos
        return cls(**data)

    def add_parameter_option(self, name, value):
        init_data = dict(name=name, value=value)
        po = ParameterOption.create_from_data(init_data)
        self.__validate_option(po)
        self.__get_option_map()[po.name] = po.value
        self.parameter_options.append(po)
        if po.parameter_definition is None:
            po.parameter_definition = self
        return po

    def has_option(self, name):
        return name in self.__get_option_map()

    def get_option(self, name, default_value=None):
        return self.__get_option_map().get(name, default_value)

    @property
    def options(self):
        return self.__get_option_map()

    def __get_option_map(self):
        if self.__po_map is None:
            self.__po_map = {}
            for po in self.parameter_options:
                self.__validate_option(po)
                self.__po_map[po.name] = po.value
        return self.__po_map

    def __validate_option(self, parameter_option):
        if not parameter_option.name in \
                    ParameterOptionRegistry.get_names(self.value_type):
            raise ValueError('Unknown parameter option name "%s" '
                             'for value type "%s".'
                             % (parameter_option.name, self.value_type))


class ParameterOption(Entity):
    """
    Option for a parameter definition.

    Holds an option name and value.
    """
    def __init__(self, parameter_definition, name, value, **kw):
        Entity.__init__(self, **kw)
        self.name = name
        self.value = value
        self.parameter_definition = parameter_definition

    @classmethod
    def create_from_data(cls, data):
        if not 'parameter_definition' in data:
            data['parameter_definition'] = None
        if not 'value' in data:
            data['value'] = None
        return cls(**data)


class Command(Entity):
    """
    Command to be executed.
    """
    #: Command definition for this command.
    command_definition = None
    #: List of parameters for this command.
    parameters = None
    #: Execution time stamp.
    timestamp = None
    #: User submitting this command.
    submitter = None
    #:
    command_type = None

    @classmethod
    def create_from_data(cls, data):
        cmd_def = data.get('command_definition')
        if not isinstance(cmd_def, CommandDefinition):
            raise ValueError('The `command_definition` argument needs to be '
                             'an instance of `CommandDefinition`.')
        # Check for parameters with names that we do not have in the
        # definitions.
        do_check_missing_mandatory = True
        prm_def_map = dict([(prm_def.name, prm_def)
                            for prm_def in cmd_def.parameter_definitions])
        prms = data.get('parameters')
        if not prms is None:
            try:
                prm_it = iter(prms)
            except TypeError:
                raise TypeError('The `parameters` argument needs to be an '
                                'iterable.')
            for prm in prm_it:
                try:
                    prm_def = prm_def_map.pop(prm.parameter_definition.name)
                except KeyError:
                    raise KeyError('Invalid parameter "%s".'
                                   % prm.parameter_definition.name)
                if prm_def.name == 'help':
                    # This is an invocation with --help.
                    do_check_missing_mandatory = False
        if do_check_missing_mandatory:
            # Check for missing mandatory parameters.
            missing_cmnd_prms = [prm_def
                                 for prm_def in prm_def_map.values()
                                 if prm_def.get_option('is_mandatory')]
            if len(missing_cmnd_prms) > 0:
                raise TypeError('No values were given for the following '
                                'mandatory parameters: %s.'
                                % ','.join([prm.name
                                            for prm in missing_cmnd_prms]))
        return cls(**data)

    def __init__(self, command_definition, submitter, parameters,
                 timestamp=None, **kw):
        if type(self) is Command:
            raise NotImplementedError('Abstract class.')
        Entity.__init__(self, **kw)
        self.command_definition = command_definition
        self.parameters = parameters
        self.submitter = submitter
        if timestamp is None:
            utc = timezone('UTC')
            timestamp = datetime.datetime.now(utc)
        self.timestamp = timestamp

    def run(self):
        raise NotImplementedError('Abstract method.')


class ShellCommand(Command):
    #: Environment variables to set for this command. Optional.
    environment = None
    #: Output generated during the execution.
    output_string = None
    #: Errors generated during the execution.
    error_string = None
    #: Exit code of the command.
    exit_code = None

    def __init__(self, command_definition, submitter, parameters,
                 environment=None, **kw):
        Command.__init__(self, command_definition, submitter, parameters,
                         **kw)
        self.command_type = 'SHELL'
        if environment is None:
            environment = {}
        self.environment = environment

    def run(self):
        cwd = self.command_definition.working_directory
        if cwd is None:
            # We use the path of the executable as default execution path.
            exc = self.command_definition.executable
            cwd = os.path.dirname(exc)
            if cwd != '':
                cwd = os.path.expandvars(cwd)
            else:
                cwd = None
        cmd_str = '%s %s' % (self.command_definition.executable,
                             self.__format_parameters(self.parameters))
        child = Popen(cmd_str,
                      shell=True,
                      cwd=cwd,
                      env=self.environment,
                      universal_newlines=True, stdout=PIPE, stderr=PIPE)
        output_string, error_string = child.communicate()
        self.output_string = output_string
        self.error_string = error_string
        self.exit_code = child.returncode

    def __format_parameters(self, parameters):
        prm_strings = []
        for prm in parameters:
            if not prm.parameter_definition.get_option('is_mandatory'):
                # Optional argument (short or long).
                if len(prm.parameter_definition.name) == 1:
                    prefix = '-%s' % prm.parameter_definition.name
                else:
                    prefix = '--%s=' % prm.parameter_definition.name
            else:
                # Positional argument.
                prefix = ''
            prm_strings.append(prefix + quote(str(prm.value)))
        return ' '.join(prm_strings)


class RestCommand(Command):
    def __init__(self, command_definition, submitter, parameters, **kw):
        Command.__init__(self, command_definition, submitter, parameters,
                         **kw)
        self.command_type = 'REST'
        self.__response = None

    def run(self):
        prms = dict([(prm.parameter_definition.name, prm.value)
                     for prm in self.parameters])
        headers = \
            {'content-type': self.command_definition.request_content_type,
             }
        cr = get_current_request()
        if not cr.authorization is None:
            headers['authorization'] = ' '.join(cr.authorization)
        self.__response = requests.request(self.command_definition.operation,
                                           self.command_definition.url,
                                           headers=headers,
                                           data=json.dumps(prms))

    @property
    def response(self):
        return self.__response

    @property
    def response_status_code(self):
        "Status code from the REST call response (integer)."
        rsp = self.__response
        return None if rsp is None else rsp.status_code

    @property
    def response_headers(self):
        "Headers from the REST call response (case-insensitive dictionary)."
        rsp = self.__response
        return None if rsp is None else rsp.headers

    @property
    def response_body(self):
        "Body from the REST call response (unicode)."
        rsp = self.__response
        return None if rsp is None else rsp.text


class Parameter(Entity):
    """
    Parameter in a command to be executed.
    """
    #: Parameter definition for this parameter.
    parameter_definition = None
    #: Value for this parameter.
    value = None

    def __init__(self, parameter_definition, value, **kw):
        Entity.__init__(self, **kw)
        self.parameter_definition = parameter_definition
        self.value = value
