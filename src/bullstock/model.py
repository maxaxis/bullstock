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

class Transaction(object):
    __storm_table__ = "transaction"

    id = Int(primary=True)
    type = Unicode()
    amount = Int()
    value = Decimal()
    trade_cost = Decimal()
    # FK
    symbol_id = Int()
    symbol = Reference(symbol_id, "Symbol.id")
    portfolio_id = Int()
    portfolio = Reference(portfolio_id, "Portfolio.id")

    def __init__(self, type, amount, value, trade_cost):
        self.type = type
        self.amount = amount
        self.value = value
        self.trade_cost = trade_cost



class FinancialInfo(object):
    __storm_table__ = "financialinfo"

    id = Int(primary=True)
    timestamp = DateTime()
    description = Unicode()
    data = Unicode()
    type = Unicode()

    def __init__(self, timestamp, description, data, type):
        self.timestamp = timestamp
        self.description = description
        self.data = data
        self.type = type


class Portfolio(object):
    __storm_table__ = "portfolio"

    id = Int(primary=True)
    name = Unicode()
    preferred_datasource = Unicode()
    preferred_currency = Unicode()
    transaction_cost = Decimal()
    symbols = ReferenceSet(
            "Portfolio.id",
            "PortfolioSymbol.portfolio_id",
            "PortfolioSymbol.symbol_id",
            "Symbol.id")

    def __init__(self, name, preferred_datasource, preferred_currency, transaction_cost):
        self.name = name
        self.preferred_datasource = preferred_datasource
        self.preferred_currency = preferred_currency
        self.transaction_cost = transaction_cost


class PortfolioSymbol(object):
    __storm_table__ = "portfolio_symbol"
    __storm_primary__ = "portfolio_id", "symbol_id"
    portfolio_id = Int()
    symbol_id = Int()

class Company(object):
    __storm_table__ = "company"

    id = Int(primary=True)
    name = Unicode()

    def __init__(self, name):
        self.name = name

class Symbol(object):
    __storm_table__ = "symbol"

    id = Int(primary=True)
    name = Unicode()
    description = Unicode()
    datasource = Unicode()
    currency = Unicode()
    # FK
    company_id = Int()
    company = Reference(company_id, Company.id)
    portfolio_id = Int()
    portfolio = Reference(portfolio_id, Portfolio.id)

    def __init__(self, name, description, datasource, currency):
        self.name = name
        self.description = description
        self.datasource = datasource
        self.currency = currency


