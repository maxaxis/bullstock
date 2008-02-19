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

from storm.locals import *
from db.dbitem import DBItem
from db.stock import Stock

class StockTransaction (DBItem):
    __storm_table__ = 'stock_transaction'
    stock_id = Int()
    stock = Reference(stock_id, Stock.id)

    type = Int()
    amount = Int()
    value = Float()
    trade_cost = Float()

    def __init__(self, type, symbol, amount, value, trade_cost):
        self.type = type
        self.symbol = symbol
        self.amount = amount
        self.value = value
        self.trade_cost = trade_cost
