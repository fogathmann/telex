"""
Entities for the telex server.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 7, 2014.
"""
import datetime

from pytz import timezone

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
    #: Command executable.
    executable = None
    #: User submitting the command.
    submitter = None
    #: Category this command definition belongs to. Optional.
    category = None
    #: Description of the purpose of this command definition. Optional.
    description = None
    #: List of parameter definitions for this command definition.
    parameter_definitions = None
    #: Environment variables to set for the command execution. Optional.
    environment = None
    #: Working directory to run the command in. Optional.
    working_directory = None

    def __init__(self, name, label, executable, submitter, category=None,
                 description=None, parameter_definitions=None,
                 environment=None, working_directory=None, **kw):
        Entity.__init__(self, **kw)
        self.name = name
        self.label = label
        self.executable = executable
        self.submitter = submitter
        self.category = category
        self.description = description
        if parameter_definitions is None:
            parameter_definitions = []
        self.parameter_definitions = parameter_definitions
        self.environment = environment
        self.working_directory = working_directory

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


class ParameterDefinition(Entity):
    """
    Parameter definition within in a command definition.
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
    #
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
    #: Environment variables to set for this command. Optional.
    environment = None
    #: Output generated during the execution.
    output_string = None
    #: Errors generated during the execution.
    error_string = None
    #: Exit code of the command.
    exit_code = None

    @classmethod
    def create_from_data(cls, data):
        prms = data.get('parameters')
        try:
            prm_it = iter(prms)
        except TypeError:
            raise TypeError('The `parameters` argument needs to be an '
                            'iterable.')
        cmd_def = data.get('command_definition')
        if not isinstance(cmd_def, CommandDefinition):
            raise ValueError('The `command_definition` argument needs to be '
                             'an instance of `CommandDefinition`.')
        # Check for parameters with names that we do not have in the
        # definitions.
        do_check_missing_mandatory = True
        prm_def_map = dict([(prm_def.name, prm_def)
                            for prm_def in cmd_def.parameter_definitions])
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
                 timestamp=None, environment=None, **kw):
        Entity.__init__(self, **kw)
        self.command_definition = command_definition
        self.parameters = parameters
        self.submitter = submitter
        if timestamp is None:
            utc = timezone('UTC')
            timestamp = datetime.datetime.now(utc)
        self.timestamp = timestamp
        self.environment = environment

    @property
    def command_string(self):
        return ' '.join([self.command_definition.executable] +
                        [str(prm) for prm in self.parameters])


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

    def __str__(self):
        if not self.parameter_definition.get_option('is_mandatory'):
            # Optional argument (short or long).
            if len(self.parameter_definition.name) == 1:
                prefix = '-%s' % self.parameter_definition.name
            else:
                prefix = '--%s=' % self.parameter_definition.name
        else:
            # Positional argument.
            prefix = ''
        return prefix + quote(str(self.value))
