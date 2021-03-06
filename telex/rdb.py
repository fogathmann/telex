"""
RDB metadata.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 31, 2014.
"""
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from everest.repositories.rdb.utils import mapper
from telex.entities import Command
from telex.entities import CommandDefinition
from telex.entities import Parameter
from telex.entities import ParameterDefinition
from telex.entities import ParameterOption
from telex.entities import RestCommand
from telex.entities import RestCommandDefinition
from telex.entities import ShellCommand
from telex.entities import ShellCommandDefinition
from sqlalchemy.schema import CheckConstraint


#from sqlalchemy.sql import literal
#from sqlalchemy.sql import select
__docformat__ = 'reStructuredText en'
__all__ = ['create_metadata',
           ]


def command_definition_slug(cls):
    return cls.name


def parameter_definition_slug(cls):
    return cls.name
#    return \
#        select([CommandDefinition.name + literal('_') + cls.name]) \
#            .where(cls.command_definition_id == CommandDefinition.id) \
#            .as_scalar()


def create_metadata(engine):
    # Table definitions.
    metadata = MetaData()
    command_definition_tbl = \
        Table('command_definition', metadata,
              Column('command_definition_id', Integer, primary_key=True),
              Column('command_definition_type', String, nullable=False,
                     default='BASE'),
              Column('name', String, nullable=False),
              Column('label', String, nullable=False),
              Column('submitter', String, nullable=False),
              Column('category', String, nullable=True),
              Column('description', String, nullable=True),
              )
    shell_cmd_def_tbl = \
        Table('shell_command_definition', metadata,
              Column('command_definition_id', Integer,
                     ForeignKey(
                        command_definition_tbl.c.command_definition_id),
                     primary_key=True,
                     nullable=False),
              Column('executable', String, nullable=False),
              Column('working_directory', String, nullable=True),
              Column('environment', String, nullable=True),
              )
    rest_cmd_def_tbl = \
        Table('rest_command_definition', metadata,
              Column('command_definition_id', Integer,
                     ForeignKey(
                        command_definition_tbl.c.command_definition_id),
                     primary_key=True,
                     nullable=False),
              Column('url', String, nullable=False),
              Column('operation', String,
                     CheckConstraint(
                                "operation IN ('GET','POST','PUT','PATCH')"),
                     nullable=False, default='POST'),
              Column('request_content_type', String, nullable=False),
              Column('response_content_type', String, nullable=False),
              )
    parameter_definition_tbl = \
        Table('parameter_definition', metadata,
              Column('parameter_definition_id', Integer, primary_key=True),
              Column('command_definition_id', Integer,
                     ForeignKey(
                        command_definition_tbl.c.command_definition_id),
                     nullable=False),
              Column('name', String, nullable=False),
              Column('label', String, nullable=False),
              Column('value_type', String, nullable=False),
              Column('description', String, nullable=True),
              )
    UniqueConstraint(parameter_definition_tbl.c.command_definition_id,
                     parameter_definition_tbl.c.name)
    parameter_option_tbl = \
        Table('parameter_option', metadata,
              Column('parameter_option_id', Integer, primary_key=True),
              Column('parameter_definition_id', Integer,
                     ForeignKey(
                        parameter_definition_tbl.c.parameter_definition_id),
                     nullable=False),
              Column('name', String, nullable=False),
              Column('value', String, nullable=False),
              )
    command_tbl = \
        Table('command', metadata,
              Column('command_id', Integer, primary_key=True),
              Column('command_type', String, nullable=False),
              Column('command_definition_id', Integer,
                     ForeignKey(
                        command_definition_tbl.c.command_definition_id),
                     nullable=False),
              Column('timestamp', DateTime, nullable=False),
              Column('submitter', String, nullable=False),
              )
    shell_cmd_tbl = \
        Table('shell_command', metadata,
              Column('command_id', Integer,
                     ForeignKey(command_tbl.c.command_id),
                     primary_key=True,
                     nullable=False),
              Column('environment', String, nullable=True),
              )
    rest_cmd_tbl = \
        Table('rest_command', metadata,
              Column('command_id', Integer,
                     ForeignKey(command_tbl.c.command_id),
                     primary_key=True,
                     nullable=False),
              )
    parameter_tbl = \
        Table('parameter', metadata,
              Column('parameter_id', Integer, primary_key=True),
              Column('parameter_definition_id', Integer,
                     ForeignKey(
                        parameter_definition_tbl.c.parameter_definition_id),
                     nullable=False),
              Column('command_id', Integer,
                     ForeignKey(command_tbl.c.command_id),
                     nullable=False),
              Column('value', String, nullable=False)
              )
    # Mapper definitions.
    cmd_def_mpr = \
        mapper(CommandDefinition, command_definition_tbl,
               id_attribute='command_definition_id',
               slug_expression=command_definition_slug,
               properties=dict(parameter_definitions=
                               relationship(ParameterDefinition,
                                            cascade_backrefs=False,
                                            back_populates=
                                                    'command_definition'),
                               ),
               polymorphic_on=
                    command_definition_tbl.c.command_definition_type,
               polymorphic_identity='BASE'
               )
    mapper(ShellCommandDefinition, shell_cmd_def_tbl,
           inherits=cmd_def_mpr,
           polymorphic_identity='SHELL')
    mapper(RestCommandDefinition, rest_cmd_def_tbl,
           inherits=cmd_def_mpr,
           polymorphic_identity='REST')
    mapper(ParameterDefinition, parameter_definition_tbl,
           id_attribute='parameter_definition_id',
           slug_expression=parameter_definition_slug,
           properties=
            dict(command_definition=
                    relationship(CommandDefinition,
                                 uselist=False,
                                 back_populates='parameter_definitions'),
                 parameter_options=
                    relationship(ParameterOption,
                                 cascade_backrefs=False,
                                 back_populates='parameter_definition'),
                 )
           )
    mapper(ParameterOption, parameter_option_tbl,
           id_attribute='parameter_option_id',
           properties=
            dict(parameter_definition=
                    relationship(ParameterDefinition,
                                 uselist=False,
                                 back_populates='parameter_options')
                 )
           )
    cmd_mpr = \
        mapper(Command, command_tbl,
               id_attribute='command_id',
               properties=dict(command_definition=
                                    relationship(CommandDefinition,
                                                 uselist=False),
                               parameters=relationship(Parameter,
                                                       cascade_backrefs=False,
                                                       back_populates=
                                                                'command'),
                               ),
               polymorphic_on=command_tbl.c.command_type,
               polymorphic_identity='BASE',
               )
    mapper(ShellCommand, shell_cmd_tbl,
           inherits=cmd_mpr,
           polymorphic_identity='SHELL')
    mapper(RestCommand, rest_cmd_tbl,
           inherits=cmd_mpr,
           polymorphic_identity='REST')
    mapper(Parameter, parameter_tbl,
           id_attribute='parameter_id',
           properties=dict(parameter_definition=
                            relationship(ParameterDefinition, uselist=False),
                               command=
                                    relationship(Command, uselist=False,
                                                 back_populates='parameters')
                           )
           )
    # Configure and initialize metadata.
    metadata.bind = engine
    metadata.create_all()
    return metadata
