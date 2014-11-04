"""
This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Oct 13, 2014.
"""
from everest.constants import ConstantGroup


__docformat__ = 'reStructuredText en'
__all__ = ['VALUE_TYPES',
           ]


class VALUE_TYPES(ConstantGroup):
    """
    Group of value type constants.
    """
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    INT = 'INT'
    DOUBLE = 'DOUBLE'
    DATETIME = 'DATETIME'
    FILE = 'FILE'
    URL = 'URL'


class ParameterOptionRegistry(object):
    __option_name_map = {}
    __option_names = set()

    @classmethod
    def register(cls, option_name, option_type, option_label, value_types):
        for value_type in value_types:
            option_items = cls.__option_name_map.setdefault(value_type, [])
            value = (option_name, option_type, option_label)
            if not value in option_items:
                option_items.append(value)
        cls.__option_names.add(option_name)

    @classmethod
    def get(cls, value_type):
        return cls.__option_name_map.get(value_type)

    @classmethod
    def get_names(cls, value_type=None):
        if not value_type is None:
            names = [item[0] for item in cls.get(value_type=value_type)]
        else:
            names = cls.__option_names
        return names


ParameterOptionRegistry.register('is_mandatory',
                                     VALUE_TYPES.BOOLEAN,
                                     'Is mandatory?', list(VALUE_TYPES))
ParameterOptionRegistry.register('default_value',
                                     VALUE_TYPES.STRING,
                                     'Default value', list(VALUE_TYPES))
ParameterOptionRegistry.register('min_length',
                                     VALUE_TYPES.INT,
                                     'Mininum length', [VALUE_TYPES.STRING])
ParameterOptionRegistry.register('max_length',
                                     VALUE_TYPES.INT,
                                     'Maximum length', [VALUE_TYPES.STRING])
ParameterOptionRegistry.register('min_value',
                                     VALUE_TYPES.INT,
                                     'Minimum value', [VALUE_TYPES.INT])
ParameterOptionRegistry.register('min_value',
                                     VALUE_TYPES.DOUBLE,
                                     'Minimum value', [VALUE_TYPES.DOUBLE])
ParameterOptionRegistry.register('max_value',
                                     VALUE_TYPES.INT,
                                     'Maximum value', [VALUE_TYPES.INT])
ParameterOptionRegistry.register('max_value',
                                     VALUE_TYPES.DOUBLE,
                                     'Maximum value', [VALUE_TYPES.DOUBLE])
ParameterOptionRegistry.register('extensions',
                                     VALUE_TYPES.STRING,
                                     'Valid extensions', [VALUE_TYPES.FILE])
