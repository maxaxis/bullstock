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

import gobject
import gtk
from gettext import gettext as _
from datetime import datetime

class DateWidget(gtk.Frame):
    def __init__(self, caption, date):
        super (DateWidget, self).__init__ (caption)

        hbox = gtk.HBox(False, 5)
        self.add(hbox)

        #TODO: use localtime format mm/dd/yyyy or dd/mm/yyyy ???

        self.entry_month = gtk.SpinButton()
        self.entry_month.set_range(0, 12)
        self.entry_month.set_increments(1.0, 10.0)
        self.entry_month.set_value(date.month)
        hbox.pack_start(self.entry_month)
        hbox.pack_start(gtk.Label('/'))

        self.entry_day = gtk.SpinButton()
        self.entry_day.set_range(0, 31)
        self.entry_day.set_increments(1.0, 10.0)
        self.entry_day.set_value(date.day)
        hbox.pack_start(self.entry_day)
        hbox.pack_start(gtk.Label('/'))

        self.entry_year = gtk.SpinButton()
        self.entry_year.set_range(2000, 10000)
        self.entry_year.set_increments(1.0, 10.0)
        self.entry_year.set_value(date.year)
        hbox.pack_start(self.entry_year)

    def get_date(self):
        date = datetime(int(self.entry_year.get_value()),
                        int(self.entry_month.get_value()),
                        int(self.entry_day.get_value()))
        return date

gobject.type_register(DateWidget)

