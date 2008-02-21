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
import shelve

from plugins import manager
from configuration import config

class Collector(object):
    def __init__(self):
        self.datasources = manager.get_plugins("datasource")
        self.current = None
        self.config = configuration.collector
        if 'cache' in self.config and self.config['cache']:
            self.cache = shelve.open(os.path.expanduser(self.config['cache']))
        else:
            self.cache = None
        
    def close(self):
        if self.cache:
            self.cache.close()

    def select_datasource(self, name):
        self.current = self.datasources[name]

    def _cached_data(self, symbol, data):
        if symbol not in self.cache:
            self.cache[symbol] = {}
            self.cache.sync()

        if data not in self.cache[symbol]:
            symbol_cache = self.cache[symbol]
            symbol_cache[data] = {}
            self.cache[symbol] = symbol_cache
            self.cache.sync()

        return self.cache[symbol][data]

    def get_quote(self, symbol, force=False):
        quote = {}

        if self.cache is not None:
            quote = self._cached_data(symbol, 'quote')

        if force or not quote:
            quote = self.current.get_quote(symbol)

            # shelve do not write changes in mutable objects
            # automatically. So we need reassign the object
            # to force shelve to write changes in file.
            # Take a look at the shelve's documentation for
            # more details.
            cache = self.cache[symbol]
            cache['quote'] = quote
            self.cache[symbol] = cache
            self.cache.sync()

        return quote

    def get_history(self, symbol, start=None, end=None, interval='d', force=False):
        # FIXME: Cache doesn't work.
        key = "%s %s %s %s" % (symbol, start, end, interval)

        if self.cache is not None:
            history_cache = self._cached_data(symbol, 'history')
            history = history_cache.get(key, {})

        if force or not history:
            history.update(self.current.get_history(symbol, start, end, interval))

            self.cache[symbol]['history'][key] = history
            self.cache.sync()

        return history


# vim:ts=4:tw=120:sm:et:si:ai

