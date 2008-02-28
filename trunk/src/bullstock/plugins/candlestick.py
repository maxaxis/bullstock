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

from plugins._base import Analysis

class Candlestick(Analysis):
    name = "candlestick"
    method = "graphic"
    
    def _validate_range(self):
        if len(self.range) >= self.quotes:
            return 1
        else:
            return 0
    def _analyze(self):
        if not _validate_range():
            return []
        intervals = []
        attempts = len(self.range) - self.quotes + 1
        cnt = 0
        while cnt <= attempts:
            interval = self.range[cnt:cnt + self.quotes]
            if _process(interval):
                intervals += result
            cnt += 1
        return intervals
    def get_patterns(self):
        return patterns

class down1(Candlestick):
    name = "Bearish Falling Three Methods"
    type = "down"
    quotes = 5
    result = "continuation"
    def __init__(self, quotes):
        self.range = quotes
    def _process(self, interval):
        pass
    def test_quotes():
        return _analyze()

plugin = Candlestick()
patterns = [down1]

# vim:ts=4:tw=120:sm:et:si:ai
