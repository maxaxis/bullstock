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
import time
import gconf
from decimal import Decimal as Dec
from gettext import gettext as _

from database import db
from model import Portfolio, Symbol, Trade
from collector import collect

class TradeList(gtk.ScrolledWindow):
    def __init__(self, hadjustment=None, vadjustment=None):
        super(TradeList, self).__init__(hadjustment, vadjustment)

        self.treeview = self._build_treeview()
        self.add(self.treeview)

    def get_selected(self):
        sel = self.treeview.get_selection()
        if sel:
            (model, iter) = sel.get_selected ()
            if iter:
                id = model.get_value(iter, 0)
                t = db.store.get(Trade, id)
                return t

        return None

    def refresh(self, portfolio):
        self._load_from_db(portfolio)

    def update_symbol(self, symbol):
        #TODO: this is very slow 
        iter = self.treeview.get_model().get_iter_first()
        while (iter):
            id = self.treeview.get_model().get_value(iter, 0)
            trade = db.store.get(Trade, id)
            if trade and trade.symbol == symbol:
                (qnt, total) = self._update_trade(self, trade)
                if qnt > 0:
                    self._update_iter(iter, trade, qnt, total)
                else:
                    self.treeview.get_model().remove(iter)


    def _update_trade(self, buy_trade):
        #TODO: this is very slow 
        trades = db.store.find(Trade, Trade.type==u'S', Trade.parent_id == buy_trade.id)
        total = 0
        qnt = buy_trade.amount
        for st in trades:
            qnt = qnt - st.amount
            total = total + ((st.value - buy_trade.value) * st.amount)

        return (qnt, total)

    def _load_from_db(self, portfolio):
        self.treeview.get_model().clear()

        btrades = db.store.find(Trade, Trade.type==u'B', Trade.portfolio_id == portfolio.id)
        for bt in btrades:
            print bt.id
            (qnt, total) = self._update_trade(bt)
            if qnt > 0:
                self._append(bt, qnt, total)

    def _update_iter(self, iter, trade, qnt, total):
        store = self.treeview.get_model ()
        store.set_value(iter, 3, qnt)
        store.set_value(iter, 6, qnt * trade.value)
        store.set_value(iter, 7, total)
        store.set_value(iter, 8, 0.0) #TODO

    def _append(self, trade, qnt, total):
        store = self.treeview.get_model ()
        i = store.append()
        store.set_value(i, 0, trade.id)
        store.set_value(i, 1, trade.symbol.name)
        store.set_value(i, 2, trade.symbol.description)
        store.set_value(i, 4, trade.value)
        store.set_value(i, 5, trade.symbol.quote['last_trade'])
        self._update_iter(i, trade, qnt, total)

    def _find_iter(self, trade):
        iter = self.treeview.get_model().get_iter_first()
        while (iter):
            id = self.treeview.get_model().get_value(iter, 0)
            if id == trade.id:
                return iter
            iter = self.treeview.get_model().iter_next(iter)

        return None


    def _build_treeview(self):
        model = gtk.ListStore(gobject.TYPE_INT,     #trade_id
                              gobject.TYPE_STRING,  #symbol name
                              gobject.TYPE_STRING,  #symbol desc
                              gobject.TYPE_INT,     #amount
                              gobject.TYPE_DOUBLE,  #buy value
                              gobject.TYPE_DOUBLE,  #current value
                              gobject.TYPE_DOUBLE,  #total buy
                              gobject.TYPE_DOUBLE,  #overall
                              gobject.TYPE_DOUBLE)  #overall %
        treeview = gtk.TreeView(model)


        #col simbol
        col = gtk.TreeViewColumn (_("Symbol"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 1)

        #col name
        col = gtk.TreeViewColumn (_("Name"))
        col.set_min_width (200)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 2)

        #col Amount
        col = gtk.TreeViewColumn (_('Amount'))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 3)

        #col buy val
        col = gtk.TreeViewColumn (_("Buy Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 4)

        #col current val
        col = gtk.TreeViewColumn (_("Current Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 5)

        #col Total Buy
        col = gtk.TreeViewColumn (_("Buy Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 6)

        #col Overall
        col = gtk.TreeViewColumn (_("Overall"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 7)

        #col Overall %
        col = gtk.TreeViewColumn (_("Overall %"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 8)

        return treeview

gobject.type_register(TradeList)

# vim:ts=4:tw=120:sm:et:si:ai
