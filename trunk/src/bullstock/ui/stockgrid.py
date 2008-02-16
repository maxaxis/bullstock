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

import gobject
import gtk

from gettext import gettext as _

class StockGridWindow(gtk.Window):
    def __init__(self, parent):
        super (StockGridWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

        self.set_transient_for (parent)
        hpaned = gtk.HPaned ()

        self.portifolio = self.build_portfolio_list ()
        scroll = gtk.ScrolledWindow (None, None)
        scroll.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add (self.portifolio)

        hpaned.pack1 (scroll, True, True)

        self.grid = self.build_stock_grid ()
        scroll = gtk.ScrolledWindow (None, None)
        scroll.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add (self.grid)

        vbox = gtk.VBox (False, 5)

        toolbar = self.build_stock_toolbar ()

        vbox.pack_start (toolbar, False)
        vbox.pack_start (scroll, True)

        hpaned.pack2 (vbox, True, True)

        self.add (hpaned)

    def build_stock_toolbar (self):

        toolbar = gtk.Toolbar ()
        item = gtk.ToolButton (gtk.STOCK_REFRESH)
        toolbar.insert (item, -1)

        toolbar.insert (gtk.SeparatorToolItem(), -1)

        item = gtk.ToolButton (gtk.STOCK_ADD)
        toolbar.insert (item, -1)

        item = gtk.ToolButton (gtk.STOCK_REMOVE)
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
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 0)

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
        col.add_attribute (cell, 'text', 1)

        #col %
        col = gtk.TreeViewColumn (_("Percent"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 2)

        #col Buy Amount
        col = gtk.TreeViewColumn (_("Buy Amount"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 3)

        #col Buy Value
        col = gtk.TreeViewColumn (_("Buy Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 4)

        #col Sell Value
        col = gtk.TreeViewColumn (_("Sell Value"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 5)

        #col Sell Amount
        col = gtk.TreeViewColumn (_("Sell Amount"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 6)

        return treeview

    def on_toolbar_refresh (self):
        None

    def on_toolbar_add (self):
        None

    def on_toolbar_remove (self):
        None

    def on_toolbar_show_chart (self):
        None



gobject.type_register(StockGridWindow)

# vim:ts=4:tw=120:sm:et:si:ai
