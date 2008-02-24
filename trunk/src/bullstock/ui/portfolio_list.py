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

from database import db
from model import Portfolio
from gettext import gettext as _

class PortfolioList(gtk.ScrolledWindow):
    __gsignals__ = {
        'selection-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    def __init__(self, hadjustment=None, vadjustment=None):
        super(PortfolioList, self).__init__ (hadjustment, vadjustment)

        self.treeview = self._build_treeview()
        self.treeview.get_selection().connect('changed', self._selection_changed)
        self.add(self.treeview)

    def load_from_db(self):
        self.treeview.get_model().clear()

        for p in db.store.find(Portfolio):
            self.append(p)

    def append(self, portfolio):
        store = self.treeview.get_model()
        i = store.append()
        store.set_value(i, 0, portfolio.id)
        store.set_value(i, 1, portfolio.name)
        store.set_value(i, 2, '0 %')

        return i

    def remove(self, portfolio):
        i = self._find_iter(portfolio)
        if i:
            self.treeview.get_model().remove(i)

    def get_selected(self):
        sel = self.treeview.get_selection()
        if sel:
            (model, iter) = sel.get_selected ()
            if iter:
                id = model.get_value(iter, 0)
                p = db.store.get(Portfolio, id)
                return p

        return None

    def _selection_changed(self, selection):
        self.emit('selection-changed')

    def _find_iter(self, portfolio):
        iter = self.treeview.get_model().get_iter_first()
        while (iter):
            id = self.treeview.get_model().get_value(iter, 0)
            if id == portfolio.id:
                return iter
            iter = self.treeview.get_model().iter_next(iter)

    def _build_treeview(self):
        model = gtk.ListStore(gobject.TYPE_INT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        treeview = gtk.TreeView(model)

        #col name
        col = gtk.TreeViewColumn(_("Name"))
        col.set_expand(True)
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', 1)
        treeview.append_column(col)

        #col percent
        col = gtk.TreeViewColumn(_("Percent"))
        col.set_alignment(1.0)
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        cell.set_property('alignment', pango.ALIGN_RIGHT)
        col.add_attribute(cell, 'text', 2)
        treeview.append_column(col)

        return treeview

gobject.type_register(PortfolioList)

# vim:ts=4:tw=120:sm:et:si:ai
