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
from copy import copy

from config import configuration
from plugins._base import DataSource
from utils import s2d


class Yahoo(DataSource):
    name = "yahoo" # configuration: data_source:yahoo

    def __init__(self):
        self.config = configuration.plugin(self)

        # defaults
        self.quote_url = self.config.get('quote_url',
                'http://download.finance.yahoo.com/d/quotes.csv')
            
        self.url_table = self.config.get('url_table',
                'http://ichart.finance.yahoo.com/table.csv?'\
                's=%(symbol)&'\
                'a=%(start_month)&'\
                'b=%(start_day)&'\
                'c=%(start_year)s&'\
                'd=%(end_month)&'\
                'e=%(end_day)s&'\
                'f=%(end_year)s&'\
                'g=%(type)&'\
                'ignore=.csv')

        try:
            columns = self.config['quote_columns']
            self.quote_columns = columns.split(",")
        except KeyError:
            self.quote_columns = ('Symbol', 'Last Trade', 'Trade Date', 'Trade Time',
                                  'Change', 'Open', 'Open?', 'Bid', 'Volume')
        self.quote_format = self.config.get('quote_format', 'sl1d1t1c1ohgv')
        self.quote_date_format = self.config.get('quote_date_format', '%m/%d/%Y')

        self.table_date_format = "%Y-%m-%d"


    def _normalize_data(self, data_dic):
        ret = copy(data_dic)
        for k, v in ret.items():
            try:
                ret[k] = float(ret[k])
            except ValueError:
                try:
                    ret[k] = s2d(ret[k], self.quote_date_format)
                except ValueError:
                    pass
        return ret

    def get_quote(self, symbol):
        query = {
            'e': '.csv',
            's': symbol,
            'f': self.quote_format,
        }
        url = "%s?%s" % (self.quote_url, urllib.urlencode(query))

        page = urllib.urlopen(url)
        quote = csv.DictReader(page, self.quote_columns, dialect='excel').next()
        page.close()

        return self._normalize_data(quote)

plugin = Yahoo()

# vim:ts=4:tw=120:sm:et:si:ai
