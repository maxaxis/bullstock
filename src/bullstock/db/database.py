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

from config import configuration

class Database (object):
    def __init__(self):

        self.filename = os.path.join(
            configuration.conf_dir,
            configuration.global.get("database", "bullstock.db")
        )

        db_exists = os.path.exists(self.filename)
        self.db = create_database("sqlite:%s" % (self.filename,))
        if not db_exists:
            self._create_tables()

        self.store = Store(self.db)

    def _create_tables(self):
        print 'Initialize Database: %s' % path

        # Please, update the datamodel before change the tables:
        # http://code.google.com/p/bullstock/wiki/DatabaseStructure

        # transactions
        self.store.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                symbol_id INTEGER,
                portfolio_id INTEGER,
                type VARCHAR,
                amount INT,
                value REAL,
                trade_cost REAL
            )""", noresult=True)

        # financial_info
        self.store.execute("""
            CREATE TABLE financial_info (
                id INTEGER PRIMARY KEY,
                company_id INTEGER,
                timestamp VARCHAR,
                description VARCHAR,
                data VARCHAR,
                type VARCHAR,
            )""", noresult=True)

        # portfolio
        self.store.execute("""
            CREATE TABLE portfolio (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                preferred_datasource VARCHAR,
                preferred_currency VARCHAR,
                transaction_cost REAL
            )""", noresult=True)

        # symbol
        self.store.execute("""
            CREATE TABLE stock (
                id INTEGER PRIMARY KEY,
                company_id INTEGER,
                portfolio_id INTEGER,
                name VARCHAR,
                description VARCHAR,
                datasource VARCHAR,
                currency VARCHAR
            )""", noresult=True)

        # company
        self.store.execute("""
            CREATE TABLE company (
                id INTEGER PRIMARY KEY,
                name VARCHAR
            )""", noresult=True)

        # history
        self.store.execute("""
            CREATE TABLE history (
                id INTEGER PRIMARY KEY,
                symbol_id INTEGER,
                timestamp VARCHAR,
                open REAL,
                high REAL,
                low REAL,
                volume INTEGER,
                type VARCHAR
            )""", noresult=True)

        # transaction
        self.store.execute("""
            CREATE TABLE stock_transaction (
                id INTEGER PRIMARY KEY,
                stock_id INTEGER,
                type INTEGER,
                amount INTEGER,
                value REAL,
                trade_cost REAL
            )""", noresult=True)

    def add_item(self, dbitem):
        self.store.add(dbitem)
        self.store.commit()


