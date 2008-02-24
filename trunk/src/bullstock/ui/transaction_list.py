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

from database import db
from model import Portfolio, Symbol, Company, Trade
from ui.date_widget import DateWidget

class TransactionList(gtk.EventBox):
    def __init__(self):
        super (TransactionList, self).__init__ ()
        vbox = gtk.VBox(False, 5)

        today = datetime.today()
        last_month = datetime(today.year, today.month - 1, today.day)

        hbox = gtk.HBox(False, 5)
        self.date_start = DateWidget(_('Start'), last_month)
        hbox.pack_start(self.date_start, False, False)

        self.date_end = DateWidget(_('End'), today)
        hbox.pack_start(self.date_end, False, False)

        btn_apply = gtk.Button(None, gtk.STOCK_APPLY)
        btn_apply.connect('clicked', self._button_apply_clicked)

        hbox.pack_start(btn_apply, False, False)
        hbox.pack_start(gtk.Label(''), True, False)

        vbox.pack_start(hbox, False)

        self.history = self._build_history_list()
        scroll = gtk.ScrolledWindow(None, None)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.history)

        vbox.pack_start(scroll, True)
        self.add(vbox)


    def load(self, date_start, date_end):
        for t in db.store.find(Trade, Trade.trade_date >= date_start and Trade.trade_date <= date_end):
            self._append(t)

    def _button_apply_clicked(self, button):
        self.load(self.date_start.get_date(), self.date_end.get_date())

    def _append(self, trade):
        model = self.history.get_model()
        i = model.append()
        model.set_value (i, 0, trade.trade_date)
        model.set_value (i, 1, trade.symbol.description)
        model.set_value (i, 2, trade.trade_cost + trade.amount * trade.value)

    def _build_history_list(self):
        model = gtk.ListStore (gobject.TYPE_STRING,  #date
                               gobject.TYPE_STRING,  #description
                               gobject.TYPE_STRING)  #value

        treeview = gtk.TreeView (model)

        #col date
        col = gtk.TreeViewColumn (_("Date"))
        cell = gtk.CellRendererText ()
        col.pack_start (cell, True)
        col.add_attribute (cell, 'text', 0)
        treeview.append_column (col)

        #col description
        col = gtk.TreeViewColumn (_("Description"))
        col.set_expand(True)
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', 1)
        treeview.append_column(col)

        #col value
        col = gtk.TreeViewColumn (_("Value"))
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', 2)
        treeview.append_column(col)

        return treeview

gobject.type_register(TransactionList)

# vim:ts=4:tw=120:sm:et:si:ai
