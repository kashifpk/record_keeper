"""
Objects that are used application wide.

These include config, connections to databases etc.
"""

import logging
import logging.config
import os.path
from configparser import ConfigParser

from zope.sqlalchemy import ZopeTransactionExtension  # pylint: disable=E
from sqlalchemy.ext.declarative import declarative_base  # pylint: disable=E
from sqlalchemy.orm import (  # pylint: disable=E0401
    scoped_session,
    sessionmaker,
)
from sqlalchemy import create_engine  # pylint: disable=E0401


class MyConfigParser(ConfigParser):  # pylint: disable=R0901
    """ConfigParser Improved."""

    def getlist(self, section, option):
        """Interpret multiple line values as list."""
        value = self.get(section, option)
        return list(filter(None, (x.strip() for x in value.splitlines())))

    def getlistint(self, section, option):
        """Return list values as integer instead of string."""
        return [int(x) for x in self.getlist(section, option)]


class App(object):
    """App like class for application wide accessible stuff."""

    _config = None
    _db = None  # postgresql
    _db_base = None
    _db_session_class = None

    def __init__(self, config_file=None, configure_logging=True):
        """Initialize application."""
        cls = self.__class__
        cls._configure_logging = configure_logging
        if config_file:
            cls._config_file = config_file
            _ = self.config
            _ = self.db

        if cls._db_base is None:
            cls._db_base = declarative_base()

    def __del__(self):
        """Cleanup objects that require proper closing."""
        cls = self.__class__
        cls._db = None

    def _create_db_session(self):
        cls = self.__class__
        if self.config:
            session_maker = scoped_session(
                sessionmaker(
                    extension=ZopeTransactionExtension(),
                    expire_on_commit=False,
                )
            )

            db_conn_str = self.config["db"]["url"]

            engine = create_engine(db_conn_str)
            session_maker.configure(bind=engine)
            cls._db_session_class = session_maker

    @property
    def config(self):
        """Get application configuration."""
        cls = self.__class__
        if hasattr(cls, "_config_file"):
            if cls._configure_logging:
                logging.config.fileConfig(cls._config_file)

            here = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            conf = MyConfigParser(defaults={"here": here})
            conf.read(cls._config_file)

            cls._config = conf

        return cls._config

    @property
    def DBBase(self):
        """Return base class for declarative models."""
        return self.__class__._db_base

    @property
    def new_db_session(self):
        """
        Create a new db session and return it.

        Future calls to self.db would return this newly generated session. Any
        previous db sessions are discarded.
        """
        cls = self.__class__
        if self._db_session_class is None:
            self._create_db_session()
            cls._db = cls._db_session_class()

        return cls._db

    @property
    def db(self):
        """Return database session if present or create new."""
        cls = self.__class__
        if cls._db is None:
            if cls._db_session_class is None:
                self._create_db_session()
            cls._db = cls._db_session_class()

        return cls._db


app = App()
