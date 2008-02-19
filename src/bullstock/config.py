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

from cStringIO import StringIO
from ConfigParser import RawConfigParser

GLOBAL_CONFIG = "/etc/bullstock.cfg"
INITIAL_CONFIG = """
[collector]
cache = ~/bullstock.dat

[datasource:yahoo]
# symbol,last trade,trade date,trade time,change,open,open?,bid,volume
url_quote = http://download.finance.yahoo.com/d/quotes.csv

# month: 00->Jan; 11->Dec
# type: d - daily; w - weekly; m - montly; v - dividends only
url_history = http://ichart.finance.yahoo.com/table.csv
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
        if type_:
            section = "%s:%s" % (type_, name)
        else:
            section = name

        ret = {}

        if not self.config.has_section(section):
            return ret

        c = self.config
        methods = (c.getint, c.getfloat, c.getboolean, c.get)

        for option in self.config.options(section):
            for method in methods:
                try:
                    ret[option] = method(section, option)
                    break
                except ValueError:
                    pass

        return ret

    def plugin(self, plugin):
        return self._get_section(plugin.plugin_type, plugin.name)

    @property
    def collector(self):
        return self._get_section("", "collector")

configuration = _Configuration()

# vim:ts=4:tw=120:sm:et:si:ai

