"""
Interfaces for the telex server.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 7, 2014.
"""

from zope.interface import Interface # pylint: disable=F0401

__docformat__ = 'reStructuredText en'
__all__ = ['ICommand',
           'ICommandDefinition',
           'IParameter',
           'IParameterDefinition',
           ]


# no __init__ pylint: disable=W0232
class ICommandDefinition(Interface):
    pass


class IShellCommandDefinition(ICommandDefinition):
    pass


class IRestCommandDefinition(ICommandDefinition):
    pass


class IParameterDefinition(Interface):
    pass


class IParameterOption(Interface):
    pass


class ICommand(Interface):
    pass


class IShellCommand(ICommand):
    pass


class IRestCommand(ICommand):
    pass


class IParameter(Interface):
    pass
# pylint: enable=W0232

