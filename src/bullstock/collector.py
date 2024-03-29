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

from plugins import manager

class _Collector(object):
    def __init__(self):
        self.datasources = manager.get_plugins("datasource")

    def get_quote(self, datasource, symbol):
        return self.datasources[datasource].get_quote(symbol)

    def get_history(self, datasource, symbol, start=None, end=None, type='d'):
        return self.datasources[datasource].get_history(symbol, start, end, type)

collect = _Collector()


# vim:ts=4:tw=120:sm:et:si:ai

