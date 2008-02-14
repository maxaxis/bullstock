#!/usr/bin/env python
# -*- encoding: utf-8 *-*
#
# Bullstock - stock market observation and analisys tool
#
# Copyright (c) 2008 Osvaldo Santana Neto <osantana@gmail.com>
#                    Luciano Wolf <luwolf@gmail.com>
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

from cStringIO import StringIO
from ConfigParser import RawConfigParser

GLOBAL_CONFIG = "/etc/bullstock.cfg"
INITIAL_CONFIG = """
[GLOBAL]

[collector]
cache = yes

[datasource:yahoo]
# symbol,last trade,trade date,trade time,change,open,open?,bid,volume
url_quote = http://download.finance.yahoo.com/d/quotes.csv?s=%(symbol)s&f=%(format)s&e=.csv

# month: 00->Jan; 11->Dec
# type: d - daily; w - weekly; m - montly; v - dividends only
url_table = http://ichart.finance.yahoo.com/table.csv?s=%(symbol)&a=%(start_month)&b=%(start_day)&c=%(start_year)s&d=%(end_month)&e=%(end_day)s&f=%(end_year)s&g=%(type)&ignore=.csv
"""

class _Configuration(object):
    def __init__(self):
        self.config = RawConfigParser()

        read = self.config.read([
            os.path.expanduser("~/.bullstock.cfg"),
            GLOBAL_CONFIG,
        ])

        if not read:
            default = StringIO(INITIAL_CONFIG)
            self.config.readfp(default)
            default.close()

    def _get_section(self, type_, name):
        section = "%s:%s" % (type_, name,)
        if not self.config.has_section(section):
            return {}
        return dict(self.config.items(section))

    def plugin(self, name):
        return self._get_section("plugin", name)

    def datasource(self, name):
        return self._get_section("datasource", name)

    def collector(self):
        if not self.config.has_section("collector"):
            return {}
        return dict(self.config.items("collector"))

configuration = _Configuration()

# vim:ts=4:tw=120:sm:et:si:ai

