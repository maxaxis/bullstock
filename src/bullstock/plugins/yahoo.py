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

import os
import csv
import urllib

from datetime import datetime
from decimal import Decimal, InvalidOperation

from configuration import config

from plugins._base import DataSource

def _isodate(x):
    return datetime.strptime(x, "%Y-%m-%d")

def _safe_decimal(x):
    try:
        return Decimal(x.strip("%"))
    except InvalidOperation, e:
        return None


class Yahoo(DataSource):
    name = "yahoo" # configuration: data_source:yahoo

    def __init__(self):
        self.config = config.plugin(self)

        # defaults
        self.url_quote = self.config.get('url_quote',
                'http://download.finance.yahoo.com/d/quotes.csv')
        self.quote_fmt = {
            "symbol":               [ "s" , lambda x: x ],
            "name":                 [ "n" , lambda x: x ],
            "last_trade":           [ "l1", _safe_decimal ],
            "date":                 [ "d1", lambda x: x ],
            "time":                 [ "t1", lambda x: x ],
            "change_points":        [ "c1", _safe_decimal ],
            "change_percent":       [ "p2", _safe_decimal ],
            "previous_close":       [ "p" , _safe_decimal ],
            "open":                 [ "o" , _safe_decimal ],
            "day_high":             [ "h" , _safe_decimal ],
            "day_low":              [ "g" , _safe_decimal ],
            "volume":               [ "v" , int ],
            "average_daily_volume": [ "a2", int ],
            "bid":                  [ "b" , _safe_decimal ],
            "ask":                  [ "a" , _safe_decimal ],
        }

        self.url_history = self.config.get('url_history',
                'http://ichart.finance.yahoo.com/table.csv')

        self.history_fmt = {
            'Date':      [ 'date',      _isodate ],
            'Open':      [ 'open',      Decimal ],
            'High':      [ 'high',      Decimal ],
            'Low':       [ 'low',       Decimal ],
            'Close':     [ 'close',     Decimal ],
            'Adj Close': [ 'adj_close', Decimal ],
            'Volume':    [ 'volume',    int ],
        }


    def get_quote(self, symbol):
        format = ''.join(x[0] for x in self.quote_fmt.values())
        query = {
            'e': '.csv',
            's': symbol,
            'f': format,
        }
        url = "%s?%s" % (self.url_quote, urllib.urlencode(query))

        page = urllib.urlopen(url)
        quote = csv.DictReader(page, self.quote_fmt.keys(), dialect='excel').next()
        page.close()

        for k, v in quote.items():
            try:
                quote[k] = self.quote_fmt[k][1](v.strip())
            except:
                quote[k] = 0

        quote['timestamp'] = datetime.strptime("%s %s" % (quote['date'], quote['time']),
                "%m/%d/%Y %I:%M%p")
        return quote


    def _normalize_record(self, record):
        ret = {}
        for k, v in record.items():
            ret[self.history_fmt[k][0]] = self.history_fmt[k][1](v)
        return ret

    def get_history(self, symbol, start, end, type):
        ret = []

        query = {
                's': symbol,
                'ignore': '.csv',
        }

        if type in 'dwm':
            query['g'] = type

        if start:
            query['a'] = start.month
            query['b'] = start.day
            query['c'] = start.year

        if end:
            query['a'] = end.month
            query['b'] = end.day
            query['c'] = end.year


        url = "%s?%s" % (self.url_history, urllib.urlencode(query))
        page = urllib.urlopen(url)

        if page.headers['Content-Type'] != "text/csv":
            page.close()
            return ret

        history = csv.DictReader(page, dialect='excel')

        for line in history:
            ret.append(self._normalize_record(line))

        page.close()

        return ret


plugin = Yahoo()

# vim:ts=4:tw=120:sm:et:si:ai
