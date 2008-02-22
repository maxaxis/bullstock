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

import sys
import pprint
from datetime import datetime, timedelta

from decimal import Decimal as Dec

from configuration import config
from database import db

from model import Portfolio, Symbol, Company

def main(*args, **kwargs):
    portfolio1 = Portfolio(u"Main Portfolio", Dec("0.10"))
    db.store.add(portfolio1)
    portfolio2 = Portfolio(u"Secondary Portfolio")
    db.store.add(portfolio2)

    symbol1 = Symbol(u"VALE5.SA", u"yahoo")
    db.store.add(symbol1)
    symbol2 = Symbol(u"PETR4.SA", u"yahoo")
    db.store.add(symbol2)
    symbol3 = Symbol(u"GGBR4.SA", u"yahoo", u"Gerdau PN")
    db.store.add(symbol3)
    symbol4 = Symbol(u"PETR3.SA", u"yahoo")
    db.store.add(symbol4)

    portfolio1.symbols.add(symbol1)
    portfolio1.symbols.add(symbol2)
    portfolio2.symbols.add(symbol2)
    portfolio2.symbols.add(symbol3)

    db.store.commit()

    print "%s: %s" % (portfolio1.name, list(portfolio1.symbols))
    print "%s: %s" % (portfolio2.name, list(portfolio2.symbols))
    print
    symbol1 = db.store.find(Symbol).order_by(Symbol.name).first()
    print symbol1.name
    print symbol1.quote

    company = db.store.find(Company, Company.name == u"PETROBRAS")[0]
    print "%s: %s" % (company.name, list(company.symbols))

    print list(symbol1.get_history(start=datetime(2008,01,01), type=u'w'))


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# vim:ts=4:tw=120:sm:et:si:ai
