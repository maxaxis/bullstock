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

from config import configuration
from plugins._base import DataSource
from utils import s2d

def _percent(x):
    return float(x.strip("%"))

def _isodate(x):
    return datetime.strptime(x, "%Y-%m-%d")

class Yahoo(DataSource):
    name = "yahoo" # configuration: data_source:yahoo

    def __init__(self):
        self.config = configuration.plugin(self)

        # defaults
        self.url_quote = self.config.get('url_quote',
                'http://download.finance.yahoo.com/d/quotes.csv')
        self.quote_fmt = {
            "symbol":               [ "s" , lambda x: x ],
            "name":                 [ "n" , lambda x: x ],
            "last_trade":           [ "l1", float ],
            "date":                 [ "d1", lambda x: x ],
            "time":                 [ "t1", lambda x: x ],
            "change_points":        [ "c1", float ],
            "change_percent":       [ "p2", _percent ],
            "previous_close":       [ "p" , float ],
            "open":                 [ "o" , float ],
            "day_high":             [ "h" , float ],
            "day_low":              [ "g" , float ],
            "volume":               [ "v" , int ],
            "average_daily_volume": [ "a2", int ],
            "bid":                  [ "b" , float ],
            "ask":                  [ "a" , float ],
        }

        self.url_history = self.config.get('url_history',
                'http://ichart.finance.yahoo.com/table.csv')

        self.history_fmt = {
            'Volume':    [ 'volume',    int ],
            'Adj Close': [ 'adj_close', float ],
            'High':      [ 'high',      float ],
            'Low':       [ 'low',       float ],
            'Date':      [ 'date',      _isodate ],
            'Close':     [ 'close',     float ],
            'Open':      [ 'open',      float ],
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
            quote[k] = self.quote_fmt[k][1](v)

        quote['timestamp'] = datetime.strptime("%s %s" % (quote['date'], quote['time']),
                "%m/%d/%Y %I:%M%p")
        return quote


    def _normalize_record(self, record):
        ret = {}
        for k, v in record.items():
            ret[self.history_fmt[k][0]] = self.history_fmt[k][1](v)
        return ret

    def get_history(self, symbol, start, end, interval):
        ret = {}

        query = {
                's': symbol,
                'g': interval,
                'ignore': '.csv',
        }

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
        history = csv.DictReader(page, dialect='excel')

        for line in history:
            record = self._normalize_record(line)
            ret[record['date']] = record

        page.close()

        return ret



plugin = Yahoo()

# vim:ts=4:tw=120:sm:et:si:ai
