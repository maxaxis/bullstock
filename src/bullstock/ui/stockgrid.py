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
from collector import Collector
from gettext import gettext as _

class StockGridWindow(gtk.Window):
    def __init__(self, parent):
        super(StockGridWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

        self.set_transient_for(parent)
        self.tips = gtk.Tooltips()

        hpaned = gtk.HPaned()

        vbox = gtk.VBox(False, 5)

        self.portfolio = self.build_portfolio_list()
        scroll = gtk.ScrolledWindow(None, None)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.portfolio)

        vbox.pack_start(scroll, True)
        vbox.pack_start(self.build_portfolio_toolbar (), False)

        hpaned.pack1(vbox, True, True)

        self.grid = self.build_stock_grid ()
        scroll = gtk.ScrolledWindow (None, None)
        scroll.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add (self.grid)

        vbox = gtk.VBox (False, 5)

        vbox.pack_start (self.build_stock_toolbar (), False)
        vbox.pack_start (scroll, True)

        hpaned.pack2 (vbox, True, True)

        self.add (hpaned)

    def build_portfolio_dlg (self, id):
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

        frame = gtk.Frame (_("Description"))
        frame.set_shadow_type (gtk.SHADOW_NONE)
        entry = gtk.Entry ()
        frame.add (entry)
        dlg.vbox.pack_start (frame, False)

        frame = gtk.Frame (_("Trade Costs"))
        frame.set_shadow_type (gtk.SHADOW_NONE)
        entry = gtk.SpinButton (None, 0.1, 2)
        frame.add (entry)
        dlg.vbox.pack_start (frame, False)

        dlg.set_resizable (False)
        if (id != -1):
            #TODO: find portfolio id on db
            # fill fields
            None

        return dlg


    def build_toolbar_button (self, stock, tip, cb=None):
        item = gtk.ToolButton(stock)
        item.set_tooltip(self.tips, tip, tip)
        if (cb != None):
            item.connect('clicked', cb, None)

        return item

    def on_new_portfolio (self, toolbutton, data):
        dlg = self.build_portfolio_dlg(-1)
        dlg.show_all()
        ret = dlg.run()
        if ret ==  gtk.RESPONSE_ACCEPT:
            portfolio = Portfolio(dlg.portfolio_name, dlg.portfolio_trade_cost)
            self._add_portfolio (portfolio)

        dlg.destroy()

    def on_remove_protfolio (self, toolbutton, data):
        None

    def build_portfolio_toolbar (self):
        toolbar = gtk.Toolbar()

        toolbar.insert (self.build_toolbar_button (gtk.STOCK_ADD, \
                                                   _("Add new portfolio"),\
                                                   self.on_new_portfolio), \
                        -1)
        toolbar.insert (self.build_toolbar_button (gtk.STOCK_REMOVE, \
                                                   _("Remove selected portfolio"), \
                                                   self.on_remove_protfolio),
                        -1)

        return toolbar

    def on_new_stock (self, toolbutton, data):
        stock = Stock (portfolio, 'GOOG')
        i = self._add_stock (stock)
        path = self.grid.get_model().get_path (i)
        col = self.grid.get_column(0)

        self.grid.set_cursor (path, col, True)


    def on_remove_stock (self, toolbutton, data):
        sel = self.grid.get_selection ()
        (model, iter) = sel.get_selected ()
        model.remove (iter)


    def build_stock_toolbar (self):

        toolbar = gtk.Toolbar ()

        toolbar.insert (self.build_toolbar_button (gtk.STOCK_REFRESH, 
                                                   _("Refresh stock values"),
                                                   None),
                        -1)
        toolbar.insert (self.build_toolbar_button (gtk.STOCK_PREFERENCES, 
                                                   _("Configure portfolio"),
                                                   None),
                        -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)
        toolbar.insert (self.build_toolbar_button (gtk.STOCK_ADD, 
                                                   _("Add new Stock"),
                                                   self.on_new_stock),
                        -1)
        toolbar.insert (self.build_toolbar_button (gtk.STOCK_REMOVE, 
                                                   _("Remove selected Stock"),
                                                   self.on_remove_stock),
                        -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)
        toolbar.insert (self.build_toolbar_button (gtk.STOCK_REDO, _("Sell selected Stock")), -1)
        toolbar.insert (self.build_toolbar_button (gtk.STOCK_UNDO, _("Buy selected Stock")), -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)

        item = gtk.ToolButton ()
        item.set_icon_name ('stock_insert-chart')
        toolbar.insert (item, -1)

        return toolbar


    def build_portfolio_list (self):

        model = gtk.ListStore (gobject.TYPE_STRING, \
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
        col.set_min_width (100)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, True)
        col.add_attribute (cell, 'text', 1)
        treeview.append_column (col)

        return treeview

    def refresh_item (self, iter, symbol = None):

        store = self.grid.get_model ()

        if (symbol):
            store.set (iter, 0, symbol.upper ())
        else:
            symbol = store.get_value (iter, 0)

        #TODO: use global collector
        collector = Collector ()
        collector.select_datasource ("yahoo")

        quote = collector.get_quote (symbol)

        store.set_value (iter, 1, quote['Symbol'])
        store.set_value (iter, 2, quote['Bid'])
        store.set_value (iter, 3, quote['Change'])

        collector.close ()



    def on_cell_simbol_edited (self, cellrenderertext, path, new_text, data):

        store = self.grid.get_model ()
        i = store.get_iter (path)
        if i:
            self.refresh_item (i, new_text.upper ())


    def build_stock_grid (self):

        model = gtk.ListStore (gobject.TYPE_STRING, \
                               gobject.TYPE_STRING, \
                               gobject.TYPE_DOUBLE, \
                               gobject.TYPE_DOUBLE, \
                               gobject.TYPE_STRING, \
                               gobject.TYPE_DOUBLE, \
                               gobject.TYPE_DOUBLE, \
                               gobject.TYPE_STRING)
        treeview = gtk.TreeView (model)


        #col simbol
        col = gtk.TreeViewColumn (_("Simbol"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        cell.set_property ('editable', True)
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 0)
        cell.connect ('edited', self.on_cell_simbol_edited, None)

        #col name
        col = gtk.TreeViewColumn (_("Name"))
        col.set_min_width (200)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 1)

        #col val
        col = gtk.TreeViewColumn (_("Last"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 2)

        #col %
        col = gtk.TreeViewColumn (_("Percent"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 3)

        #col Buy Amount
        col = gtk.TreeViewColumn (_("Buy Amount"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 4)

        #col Buy Value
        col = gtk.TreeViewColumn (_("Buy Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 5)

        #col Sell Value
        col = gtk.TreeViewColumn (_("Sell Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 6)

        #col Sell Amount
        col = gtk.TreeViewColumn (_("Sell Amount"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 7)

        return treeview

    def on_toolbar_refresh (self):
        None

    def on_toolbar_add (self):
        None

    def on_toolbar_remove (self):
        None

    def on_toolbar_show_chart (self):
        None

    def _add_stock(self, stock):
        application.database.add_item(portfolio)

        store = self.grid.get_model ()
        i = store.append ()
        store.set_value (i, 0, stock.symbol)

        return i

    def _add_portfolio(self, portfolio):
        application.database.add_item(portfolio)

        store = self.portfolio.get_model()
        i = store.append()
        store.set_value(i, 0, portfolio.name)
        store.set_value(i, 1, '0 %')

gobject.type_register(StockGridWindow)

# vim:ts=4:tw=120:sm:et:si:ai
