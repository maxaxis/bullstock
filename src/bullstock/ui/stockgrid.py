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
import pango
import time
from threading import Thread
from threading import Condition
from decimal import Decimal as Dec
from gettext import gettext as _

from database import db
from model import Portfolio, Symbol, Company, Trade
from collector import collect
from ui.trade_dialog import TradeDialog

class _SymbolMonitor(Thread):
    class SymbolData:
        def __init__(self, symbol, cb, data):
            self.symbol = symbol
            self.symbol_name = symbol.name
            self.datasource = symbol.datasource
            self.cb = cb
            self.data = data

    def __init__(self, timeout=5):
        Thread.__init__(self)

        self.sleep_function = None
        self.symbols = []
        self.running = False
        self.timeout = timeout
        self.started = False
        self.cond = Condition()
        self.idle_id = 0
        self.timeout_id = 0

    def _start(self):
        self.running = True
        if not self.started:
            self.started = True
            self.start()

    def stop(self):
        self.running = False
        self.cond.acquire()
        self.cond.notifyAll()
        self.cond.release()
        self.join()

        if self.timeout_id:
            gobject.source_remove(self.timeout_id)
            self.timeout_id = 0

        if self.idle_id:
            gobject.source_remove(self.idle_id)
            self.idle_id = 0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def get_timeout(self):
        return self.timeout

    def append(self, symbol, update_cb, data):
        self.symbols.append(self.SymbolData(symbol, update_cb, data))
        self._start()

    def remove(self, symbol):
        for sd in self.symbols:
            if sd.symbol == symbol:
                self.symbols.remove(sd)
                break

    def clear(self):
        self.stop()
        self.symbols = []

    def set_sleep_function(self, sleep_func):
        self.sleep_function = sleep_func

    def run(self):
        self.cond.acquire()
        while self.running:
            for sd in self.symbols:
                q = collect.get_quote(sd.datasource, sd.symbol_name)
                if self.running:
                    gobject.idle_add(self._idle_emit_signal, sd, q)
                else:
                    break

            self.idle_id = gobject.idle_add(self.sleep_function)
            if self.running:
                self.timeout_id = gobject.timeout_add(1000 * self.timeout, self._timeout_cb)
            self.cond.wait()

    def _timeout_cb(self):
        self.cond.acquire()
        self.timeout_id = 0
        self.cond.notifyAll()
        self.cond.release()

    def _idle_emit_signal(self, symbol_data, q):
        symbol_data.cb(symbol_data.symbol, q, symbol_data.data)


class StockGridWindow(gtk.Window):
    def __init__(self, parent):
        super(StockGridWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

        self.symbol_monitor = None
        self.set_transient_for(parent)
        self.tips = gtk.Tooltips()
        self.selected_portfolio = None

        hpaned = gtk.HPaned()
        hpaned.set_position(35)

        vbox = gtk.VBox(False, 5)

        self.portfolio = self._build_portfolio_list()
        self.portfolio.get_selection().connect('changed',
                                               self._on_portfolio_changed)
        scroll = gtk.ScrolledWindow(None, None)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.portfolio)
        self._load_portfolios()

        vbox.pack_start(scroll, True)
        vbox.pack_start(self._build_portfolio_toolbar (), False)

        hpaned.pack1(vbox, True, True)

        self.grid = self._build_symbol_grid ()
        scroll = gtk.ScrolledWindow (None, None)
        scroll.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add (self.grid)

        vbox = gtk.VBox(False, 5)

        vbox.pack_start(self._build_symbol_toolbar (), False)
        vbox.pack_start(scroll, True)

        hpaned.pack2(vbox, True, True)

        vbox = gtk.VBox(False, 5)
        vbox.pack_start(hpaned, True, True)

        self.statusbar = gtk.HBox(False, 5)
        self.statusbar.set_size_request(-1, 20)
        self.progressbar = gtk.ProgressBar()
        self.statusbar.pack_start(self.progressbar, False, True, 5)
        self.statusbar.pack_start(gtk.Label(''), True, True, 5)
        vbox.pack_start(self.statusbar, False, True, 5)

        self.add(vbox)
        self.show_all()
        self.progressbar.hide_all()

        self.connect('delete-event', self._on_delete_event)

    def _on_delete_event(self, widget, event):
        if self.symbol_monitor:
            self.symbol_monitor.stop()

    def _on_portfolio_changed(self, treeselection):
        (model, iter) = treeselection.get_selected()
        if iter:
            id = model.get_value(iter, 0)
            self.selected_portfolio = db.store.get(Portfolio, id)
            if self.selected_portfolio:
                self._load_symbols(self.selected_portfolio)

    def _build_portfolio_dlg (self, id):
        dlg = gtk.Dialog(_("Portfolio"),
                         self,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        frame = gtk.Frame(_("Name"))
        frame.set_shadow_type (gtk.SHADOW_NONE)
        entry = gtk.Entry ()
        frame.add (entry)
        dlg.vbox.pack_start (frame, False)
        dlg.portfolio_name = entry

        frame = gtk.Frame (_("Description"))
        frame.set_shadow_type (gtk.SHADOW_NONE)
        entry = gtk.Entry ()
        frame.add (entry)
        dlg.vbox.pack_start (frame, False)
        dlg.portfolio_description = entry

        frame = gtk.Frame (_("Trade Costs"))
        frame.set_shadow_type (gtk.SHADOW_NONE)
        entry = gtk.SpinButton (None, 0.0, 2)
        entry.set_increments(0.5, 1.0)
        #TODO: get max float const
        entry.set_range(0.0, 100000.0)
        frame.add (entry)
        dlg.vbox.pack_start (frame, False)
        dlg.portfolio_trade_cost = entry

        dlg.set_resizable (False)
        if (id != -1):
            #TODO: find portfolio id on db
            # fill fields
            None

        return dlg


    def _build_toolbar_button (self, symbol, tip, cb=None):
        item = gtk.ToolButton(symbol)
        item.set_tooltip(self.tips, tip, tip)
        if (cb != None):
            item.connect('clicked', cb, None)

        return item

    def _on_new_portfolio (self, toolbutton, data):
        dlg = self._build_portfolio_dlg(-1)
        dlg.show_all()
        ret = dlg.run()
        if ret ==  gtk.RESPONSE_ACCEPT:
            portfolio = Portfolio(unicode(dlg.portfolio_name.get_text()),
                                  Dec(str(dlg.portfolio_trade_cost.get_value())))
            db.store.add(portfolio)
            db.store.commit()
            self._append_portfolio (portfolio)

        dlg.destroy()

    def _on_remove_protfolio (self, toolbutton, data):
        sel = self.portfolio.get_selection()
        if sel:
            (model, iter) = sel.get_selected ()
            id = model.get_value(iter, 0)
            p = db.store.get(Portfolio, id)
            if p:
                db.store.remove(p)
                db.store.commit()
            model.remove(iter)



    def _build_portfolio_toolbar (self):
        toolbar = gtk.Toolbar()

        toolbar.insert (self._build_toolbar_button (gtk.STOCK_ADD,
                                                   _("Add new portfolio"),
                                                   self._on_new_portfolio),
                        -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REMOVE,
                                                   _("Remove selected portfolio"),
                                                   self._on_remove_protfolio),
                        -1)

        return toolbar

    def _on_new_symbol (self, toolbutton, data):
        if self.selected_portfolio:
            symbol = Symbol (u'GOOG', u'yahoo')
            db.store.add(symbol)
            self.selected_portfolio.symbols.add(symbol)
            db.store.commit()

            i = self._append_symbol (symbol)

            # start edit cell
            path = self.grid.get_model().get_path (i)
            col = self.grid.get_column(0)
            self.grid.set_cursor (path, col, True)

    def _get_selected_symbol (self):
        sel = self.grid.get_selection ()
        (model, iter) = sel.get_selected ()
        if iter:
            id = model.get_value(iter, 0)
            s = db.store.get(Symbol, id)
            return (s, model, iter)

        return (None, None, None)


    def _on_remove_symbol (self, toolbutton, data):
        (s, iter, model) = self._get_selected_symbol()

        if s:
            db.store.remove(s)
            db.store.commit()
            model.remove(iter)

    def _process_trade(self, trade):
        print trade.symbol
        print trade.symbol.amount
        if not trade.symbol.amount:
            trade.symbol.amount = 0
        if trade.type == 'S':
            trade.symbol.amount =  trade.symbol.amount - trade.amount
        else:
            trade.symbol.amount =  trade.symbol.amount + trade.amount

        trade.portfolio = self.selected_portfolio
        db.store.add(trade)
        db.store.commit()

    def _on_sell_symbol(self, toolbutton, data):
        (s, model, iter) = self._get_selected_symbol()

        if s:
            price = model.get_value(iter, 3)
            dlg = TradeDialog(self, self.selected_portfolio, s, 'S', price)
            dlg.show_all()
            while (True):
                if dlg.run() == gtk.RESPONSE_OK:
                    if dlg.valid():
                        trade = dlg.get_trade_object()
                        self._process_trade(trade)
                        break
                else:
                    break

            dlg.destroy()

    def _on_buy_symbol(self, toolbutton, data):
        (s, model, iter) = self._get_selected_symbol()

        if s:
            price = model.get_value(iter, 3)
            dlg = TradeDialog(self, self.selected_portfolio, s, 'B', price)
            dlg.show_all()

            while (True):
                if dlg.run() == gtk.RESPONSE_OK:
                    if dlg.valid():
                        trade = dlg.get_trade_object()
                        self._process_trade(trade)
                        break
                else:
                    break

            dlg.destroy()

    def _build_symbol_toolbar (self):

        toolbar = gtk.Toolbar ()

        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REFRESH, 
                                                   _("Refresh symbol values"),
                                                   None),
                        -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_PREFERENCES, 
                                                   _("Configure portfolio"),
                                                   None),
                        -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_ADD, 
                                                   _("Add new Symbol"),
                                                   self._on_new_symbol),
                        -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REMOVE, 
                                                   _("Remove selected Symbol"),
                                                   self._on_remove_symbol),
                        -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REDO, 
                                                    _("Sell selected Symbol"),
                                                    self._on_sell_symbol),
                        -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_UNDO, 
                                                    _("Buy selected Symbol"),
                                                    self._on_buy_symbol),
                        -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)

        item = gtk.ToolButton ()
        item.set_icon_name ('stock_insert-chart')
        toolbar.insert (item, -1)

        return toolbar


    def _build_portfolio_list (self):

        model = gtk.ListStore (gobject.TYPE_INT,
                               gobject.TYPE_STRING,
                               gobject.TYPE_STRING)

        treeview = gtk.TreeView (model)

        #col name
        col = gtk.TreeViewColumn (_("Name"))
        col.set_expand (True)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, True)
        col.add_attribute (cell, 'text', 1)
        treeview.append_column (col)

        #col percent
        col = gtk.TreeViewColumn (_("Percent"))
        col.set_alignment(1.0)
        cell = gtk.CellRendererText ()
        col.pack_start(cell, True)
        cell.set_property('alignment', pango.ALIGN_RIGHT)
        col.add_attribute(cell, 'text', 2)
        treeview.append_column(col)

        return treeview

    def _symbol_updated(self, symbol, q, i):
        self.progressbar.show_all()
        self.progressbar.pulse()

        if q:
            symbol.description  = unicode(q['name'])
            store = self.grid.get_model ()
            if store:
                store.set_value (i, 1, symbol.name)
                store.set_value (i, 2, symbol.description)
                store.set_value (i, 3, q['last_trade'])
                store.set_value (i, 4, q['change_percent'])
                store.set_value (i, 5, 0.0)
                store.set_value (i, 6, q['bid'])
                store.set_value (i, 7, q['ask'])
                store.set_value (i, 8, 0.0)

    def _refresh_item (self, i, symbol):
        store = self.grid.get_model ()
        store.set_value (i, 1, symbol.name)
        self.symbol_monitor.append(symbol, self._symbol_updated, i)

    def _on_cell_simbol_edited (self, cellrenderertext, path, new_text, data):
        store = self.grid.get_model ()
        i = store.get_iter (path)
        if i:
            id = store.get_value(i, 0)
            symbol = db.store.get(Symbol, id)
            if symbol:
               symbol.name = unicode(new_text.upper())
               db.store.commit()
               self._refresh_item (i, symbol)


    def _build_symbol_grid (self):

        model = gtk.ListStore (gobject.TYPE_INT,
                               gobject.TYPE_STRING,
                               gobject.TYPE_STRING,
                               gobject.TYPE_DOUBLE,
                               gobject.TYPE_DOUBLE,
                               gobject.TYPE_STRING,
                               gobject.TYPE_DOUBLE,
                               gobject.TYPE_DOUBLE,
                               gobject.TYPE_STRING)
        treeview = gtk.TreeView (model)


        #col simbol
        col = gtk.TreeViewColumn (_("Simbol"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        cell.set_property ('editable', True)
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 1)
        cell.connect ('edited', self._on_cell_simbol_edited, None)

        #col name
        col = gtk.TreeViewColumn (_("Name"))
        col.set_min_width (200)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 2)

        #col val
        col = gtk.TreeViewColumn (_("Last"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 3)

        #col %
        col = gtk.TreeViewColumn (_("Percent"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 4)

        #col Buy Amount
        col = gtk.TreeViewColumn (_("Buy Amount"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 5)

        #col Buy Value
        col = gtk.TreeViewColumn (_("Buy Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 6)

        #col Sell Value
        col = gtk.TreeViewColumn (_("Sell Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 7)

        #col Sell Amount
        col = gtk.TreeViewColumn (_("Sell Amount"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 8)

        return treeview

    def _on_toolbar_refresh (self):
        None

    def _on_toolbar_add (self):
        None

    def _on_toolbar_remove (self):
        None

    def _on_toolbar_show_chart (self):
        None

    def _append_symbol(self, symbol):
        store = self.grid.get_model ()
        i = store.append ()
        store.set_value (i, 0, symbol.id)
        store.set_value (i, 1, symbol.name)
        store.set_value (i, 2, symbol.description)

        return i

    def _append_portfolio(self, portfolio):
        store = self.portfolio.get_model()
        i = store.append()
        store.set_value(i, 0, portfolio.id)
        store.set_value(i, 1, portfolio.name)
        store.set_value(i, 2, '0 %')

        return i

    def _load_symbols(self, portfolio):

        #create symbol monitor
        if self.symbol_monitor:
            self.symbol_monitor.clear()

        self.symbol_monitor = _SymbolMonitor()
        self.symbol_monitor.set_sleep_function(self._hide_statusbar)

        self.grid.get_model().clear()
        for s in portfolio.symbols:
            i = self._append_symbol(s)
            self._refresh_item (i, s)

    def _load_portfolios(self):
        self.portfolio.get_model().clear()
        for p in db.store.find(Portfolio):
            self._append_portfolio(p)

    def _hide_statusbar(self):
        self.progressbar.hide_all()

gobject.type_register(StockGridWindow)

# vim:ts=4:tw=120:sm:et:si:ai
