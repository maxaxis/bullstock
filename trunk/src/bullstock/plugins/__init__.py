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
import glob

from _base import *

class PluginLoaderException(Exception):
    pass

class _Manager(object):
    def __init__(self):
        self.plugins = self._get_plugins()

    def _get_plugins(self):
        plugins_path = "%s/*.py" % (os.path.dirname(__file__),)

        plugins = {}
        for fname in glob.glob(plugins_path):
            name = os.path.splitext(os.path.basename(fname))[0]

            # skip system modules
            if name.startswith("_"):
                continue

            module = __import__("plugins.%s" % (name,), fromlist="plugin")

            if 'plugin' not in module.__dict__:
                raise PluginLoaderException("Module '%s' is not a plugin." % (name,))

            plugin = module.plugin

            if plugin.plugin_type not in plugins:
                plugins[plugin.plugin_type] = {}

            if name in plugins[plugin.plugin_type]:
                raise PluginLoaderException("Plugin '%s' already loaded." % (name,))

            plugins[plugin.plugin_type][name] = plugin

        return plugins

    def get_plugin(self, plugin_type, name):
        return self.plugins[plugin_type][name]

    def get_plugins(self, plugin_type):
        return {'yahoo': None}
        return self.plugins[plugin_type].value()


manager = _Manager()

# vim:ts=4:tw=120:sm:et:si:ai
