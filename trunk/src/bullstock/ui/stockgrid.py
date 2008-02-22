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
from decimal import Decimal as Dec
from gettext import gettext as _

from database import db
from model import Portfolio, Symbol, Company

class StockGridWindow(gtk.Window):
    def __init__(self, parent):
        super(StockGridWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

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

        vbox = gtk.VBox (False, 5)

        vbox.pack_start (self._build_symbol_toolbar (), False)
        vbox.pack_start (scroll, True)

        hpaned.pack2 (vbox, True, True)

        self.add (hpaned)

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
        entry = gtk.SpinButton (None, 0.1, 2)
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


    def _on_remove_symbol (self, toolbutton, data):
        sel = self.grid.get_selection ()
        (model, iter) = sel.get_selected ()

        if iter:
            id = model.get_value(iter, 0)
            s = db.store.get(Symbol, id)
            if id:
                db.store.remove(p)
                db.store.commit()
            model.remove(iter)

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
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REDO, _("Sell selected Symbol")), -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_UNDO, _("Buy selected Symbol")), -1)
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

    def _refresh_item (self, i, symbol):

        q = symbol.quote
        if q:
            symbol.description  = unicode(q['name'])
            store = self.grid.get_model ()
            store.set_value (i, 0, symbol.id)
            store.set_value (i, 1, symbol.name)
            store.set_value (i, 2, symbol.description)
            store.set_value (i, 3, q['last_trade'])
            store.set_value (i, 4, q['change_percent'])
            store.set_value (i, 5, 0.0)
            store.set_value (i, 6, q['bid'])
            store.set_value (i, 7, q['ask'])
            store.set_value (i, 8, 0.0)

    def _on_cell_simbol_edited (self, cellrenderertext, path, new_text, data):

        store = self.grid.get_model ()
        i = store.get_iter (path)
        if i:
            id = store.get_value(i, 0)
            symbol = db.store.get(Symbol, id)
            if symbol:
               symbol.name = unicode(new_text.upper())
               self._refresh_item (i, symbol)
               db.store.commit()


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
        self.grid.get_model().clear()
        for s in portfolio.symbols:
            i = self._append_symbol(s)
            self._refresh_item (i, s)

    def _load_portfolios(self):
        self.portfolio.get_model().clear()
        for p in db.store.find(Portfolio):
            self._append_portfolio(p)

gobject.type_register(StockGridWindow)

# vim:ts=4:tw=120:sm:et:si:ai
