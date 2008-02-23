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

import re
from datetime import timedelta

from storm.locals import *

from collector import collect
from database import db

class StockTransaction(Storm):
    __storm_table__ = "stocktransaction"

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


class FinancialInfo(Storm):
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


class Portfolio(Storm):
    __storm_table__ = "portfolio"

    id = Int(primary=True)
    name = Unicode()
    transaction_cost = Decimal()

    def __init__(self, name, transaction_cost=0):
        self.name = name
        self.transaction_cost = transaction_cost

class Symbol(Storm):
    __storm_table__ = "symbol"

    id = Int(primary=True)
    name = Unicode()
    description = Unicode()
    datasource = Unicode()
    # FK
    company_id = Int()
    company = Reference(company_id, "Company.id")

    def __init__(self, name, datasource, description=u""):
        self.name = name
        self.datasource = datasource

        q = self.quote
        print q

        full_name = unicode(self.quote['name'])
        striped_name = unicode(re.sub(" +-[A-Z]*$", "", full_name).strip())
        companies = list(db.store.find(
            Company,
            Company.name == striped_name
        ))

        if companies:
            self.company = companies[0]
        else:
            self.company = Company(striped_name)

        if description:
            self.description = description
        else:
            self.description = full_name

    def __repr__(self):
        return "<Symbol '%s'>" % (self.name,)

    @property
    def quote(self):
        return collect.get_quote(self.datasource, self.name)

    def get_quote(self):
        return collect.get_quote(self.datasource, self.name)

    def get_history(self, start=None, end=None, type=u'd'):
        self.refresh_history(type)

        query = [
            History,
            History.symbol == self,
            History.type == type,
        ]

        if start is not None:
            query.append(History.timestamp >= start)

        if end is not None:
            query.append(History.timestamp <= end)

        return db.store.find(*query).order_by(History.timestamp)


    def refresh_history(self, type=u'd'):
        last_record = db.store.find(
            History,
            History.symbol == self,
            History.type == type
        ).order_by(
            Desc(History.timestamp)
        ).first()

        if not last_record:
            start = None
        else:
            start = last_record.timestamp + timedelta(1)

        update = collect.get_history(self.datasource, self.name, start=start, type=type)
        for row in update:
            db.store.add(History(
                self,
                row['date'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                type
            ))

        db.store.commit()

class PortfolioSymbol(Storm):
    __storm_table__ = "portfolio_symbol"
    __storm_primary__ = "portfolio_id", "symbol_id"
    portfolio_id = Int()
    symbol_id = Int()

Portfolio.symbols = ReferenceSet(
            Portfolio.id,
            PortfolioSymbol.portfolio_id,
            PortfolioSymbol.symbol_id,
            Symbol.id)


class Company(Storm):
    __storm_table__ = "company"

    id = Int(primary=True)
    name = Unicode()

    def __init__(self, name):
        self.name = name

Company.symbols = ReferenceSet(Company.id, Symbol.company_id)

class History(Storm):
    __storm_table__ = "history"

    id = Int(primary=True)
    timestamp = DateTime()
    open = Decimal()
    high = Decimal()
    low = Decimal()
    close = Decimal()
    volume = Int()
    type = Unicode() # d/w/m
    # FK
    symbol_id = Int()
    symbol = Reference(symbol_id, "Symbol.id")

    def __init__(self, symbol, timestamp, open, high, low, close, volume, type):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.type = type

    def __repr__(self):
        return "<History '%s' %s % 7.2f-% 7.2f-% 7.2f-% 7.2f-%10d>" % (
            self.type,
            self.timestamp.strftime("%Y-%m-%d"),
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
        )

# vim:ts=4:tw=120:sm:et:si:ai
