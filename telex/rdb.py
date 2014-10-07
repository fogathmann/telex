"""
RDB metadata.

This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 31, 2014.
"""
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
#from sqlalchemy.sql import literal
#from sqlalchemy.sql import select

from everest.repositories.rdb.utils import mapper
from telex.entities import Command
from telex.entities import CommandDefinition
from telex.entities import Parameter
from telex.entities import ParameterDefinition


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
              Column('name', String, nullable=False),
              Column('label', String, nullable=False),
              Column('executable', String, nullable=False),
              Column('submitter', String, nullable=False),
              Column('category', String, nullable=True),
              Column('description', String, nullable=True),
              Column('working_directory', String),
              Column('environment', String),
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
              Column('description', String, nullable=True),
              Column('value_type', String, nullable=False),
              Column('default_value', String),
              Column('is_mandatory', Boolean, nullable=False, default=False),
              )
    UniqueConstraint(parameter_definition_tbl.c.command_definition_id,
                     parameter_definition_tbl.c.name)
    command_tbl = \
        Table('command', metadata,
              Column('command_id', Integer, primary_key=True),
              Column('command_definition_id', Integer,
                     ForeignKey(
                        command_definition_tbl.c.command_definition_id),
                     nullable=False),
              Column('timestamp', DateTime, nullable=False),
              Column('submitter', String, nullable=False),
              Column('environment', String),
              )
    parameter_tbl = \
        Table('parameter', metadata,
              Column('parameter_id', Integer, primary_key=True),
              Column('parameter_definition_id', Integer,
                     ForeignKey(
                        parameter_definition_tbl.c.parameter_definition_id),
                     nullable=False),
              Column('value', String, nullable=False)
              )
    command_parameter_tbl = \
        Table('command_parameter', metadata,
              Column('command_id', Integer,
                     ForeignKey(command_tbl.c.command_id),
                     primary_key=True),
              Column('parameter_id', Integer,
                     ForeignKey(parameter_tbl.c.parameter_id),
                     primary_key=True),
              )
    # Mapper definitions.
    mapper(CommandDefinition, command_definition_tbl,
           id_attribute='command_definition_id',
           slug_expression=command_definition_slug,
           properties=dict(parameter_definitions=
                            relationship(ParameterDefinition,
                                         back_populates='command_definition'),
                           )
           )
    mapper(ParameterDefinition, parameter_definition_tbl,
           id_attribute='parameter_definition_id',
           slug_expression=parameter_definition_slug,
           properties=
            dict(command_definition=
                    relationship(CommandDefinition,
                                 uselist=False,
                                 back_populates='parameter_definitions')
                 )
           )
    mapper(Command, command_tbl,
           id_attribute='command_id',
           properties=dict(command_definition=relationship(CommandDefinition,
                                                           uselist=False),
                           parameters=relationship(Parameter,
                                                   secondary=
                                                        command_parameter_tbl),
                           ),
           )
    mapper(Parameter, parameter_tbl,
           id_attribute='parameter_id',
           properties=dict(parameter_definition=
                            relationship(ParameterDefinition, uselist=False)
                           )
           )
    # Configure and initialize metadata.
    metadata.bind = engine
    metadata.create_all()
    return metadata
