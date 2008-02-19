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


import gobject
import os.path
from storm.locals import *

from db.portfolio import Portfolio
from db.stock import Stock
from db.transaction import StockTransaction


class Database (object):
    file_name = None
    db = None
    store = None

    def __init__(self, file_name):
        self.file_name = file_name

    def create (self):
        dir = os.path.join (os.path.expanduser('~'), '.bullstock/')
        if not os.path.exists(dir):
            os.mkdir(dir)

        path = os.path.join(dir, self.file_name)
        new_db = not os.path.exists(path)
        print path
        self.db = create_database("sqlite:" + path)
        self.store = Store(self.db)

        if new_db:
            print 'Initialize Database: %s' % path
            self._build_db()

    def add_item(self, dbitem):
        self.store.add(dbitem)
        self.store.commit()

    def _build_db (self):

        #portfolio
        self.store.execute("CREATE TABLE portfolio "
                           "(id INTEGER PRIMARY KEY, name VARCHAR, trade_cost REAL)",
                            noresult=True)

        #stock
        self.store.execute("CREATE TABLE stock "
                           "(id INTEGER PRIMARY KEY, portfolio_id INTEGER, symbol VARCHAR)",
                           noresult=True)

        #transaction
        self.store.execute("CREATE TABLE stock_transaction "
                           "(id INTEGER PRIMARY KEY, stock_id INTEGER, type INTEGER, amount INTEGER, value REAL, trade_cost REAL)",
                           noresult=True)

