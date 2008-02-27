#!/usr/bin/env python
# -*- encoding: utf-8 *-*
#
# Bullstock - stock market observation and analisys tool
#
# Copyright (c) 2008 Osvaldo Santana Neto <osantana@gmail.com>
#                    Luciano Wolf <lucianomw@gmail.com>
#                    Renato Filho <renatox@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os.path
from storm.locals import *

from configuration import config

class _Database(object):
    def __init__(self):

        self.filename = os.path.join(
            config.conf_dir,
            config.global_conf.get("database", "bullstock.db")
        )

        db_exists = os.path.exists(self.filename)
        self.db = create_database("sqlite:%s" % (self.filename,))
        self.store = Store(self.db)

        if not db_exists:
            self._create_tables()
            self._insert_default_values()

    def _insert_default_values(self):
        self.store.execute("""
            INSERT INTO portfolio (name, transaction_cost)
            VALUES ('bullstock-watch', 0.00)
            """, noresult=True)
        self.store.commit()

    def _create_tables(self):
        print 'Initialize Database: %s' % (self.filename,)

        # Please, update the datamodel before change the tables:
        # http://code.google.com/p/bullstock/wiki/DatabaseStructure

        # trade
        self.store.execute("""
            CREATE TABLE trade (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                symbol_id INTEGER,
                portfolio_id INTEGER,
                type TEXT,
                amount INT,
                value TEXT,
                trade_cost TEXT,
                trade_date TEXT
            )""", noresult=True)

        # financialinfo
        self.store.execute("""
            CREATE TABLE financialinfo (
                id INTEGER PRIMARY KEY,
                company_id INTEGER,
                timestamp TEXT,
                description TEXT,
                data TEXT,
                type TEXT
            )""", noresult=True)

        # portfolio
        self.store.execute("""
            CREATE TABLE portfolio (
                id INTEGER PRIMARY KEY,
                name TEXT,
                transaction_cost TEXT
            )""", noresult=True)

        # portfolio-symbol (n-to-m relationship)
        self.store.execute("""
            CREATE TABLE portfolio_symbol (
                portfolio_id INTEGER,
                symbol_id INTEGER
            )""", noresult=True)

        # symbol
        self.store.execute("""
            CREATE TABLE symbol (
                id INTEGER PRIMARY KEY,
                company_id INTEGER,
                name TEXT,
                description TEXT,
                datasource TEXT
            )""", noresult=True)

        # company
        self.store.execute("""
            CREATE TABLE company (
                id INTEGER PRIMARY KEY,
                name TEXT
            )""", noresult=True)

        # history
        self.store.execute("""
            CREATE TABLE history (
                id INTEGER PRIMARY KEY,
                symbol_id INTEGER,
                timestamp TEXT,
                open TEXT,
                high TEXT,
                low TEXT,
                close TEXT,
                volume INTEGER,
                type TEXT
            )""", noresult=True)

        self.store.commit()

    def add(self, item):
        self.store.add(item)
        self.store.commit()


db = _Database()


# vim:ts=4:tw=120:sm:et:si:ai
