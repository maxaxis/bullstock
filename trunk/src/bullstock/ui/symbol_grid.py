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
from threading import Thread
from threading import Condition
from decimal import Decimal as Dec
from gettext import gettext as _

from database import db
from model import Portfolio, Symbol
from collector import collect

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

        self.paused = False
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
        self.pause()
        for sd in self.symbols:
            if sd.symbol == symbol:
                self.symbols.remove(sd)
                break
        self.unlock()

    def clear(self):
        self.stop()
        self.symbols = []

    def pause(self):
        self.paused = True
        self.cond.acquire()
        self.paused = False
        if self.timeout_id:
            gobject.source_remove(self.timeout_id)
            self.timeout_id = 0

        if self.idle_id:
            gobject.source_remove(self.idle_id)
            self.idle_id = 0

    def unlock(self):
        self.cond.notifyAll()
        self.cond.release()

    def set_sleep_function(self, sleep_func):
        self.sleep_function = sleep_func

    def run(self):
        self.cond.acquire()
        while self.running:
            for sd in self.symbols:
                try:
                    q = collect.get_quote(sd.datasource, sd.symbol_name)
                except:
                    q = None

                if not self.paused and self.running:
                    gobject.idle_add(self._idle_emit_signal, sd, q)
                else:
                    break

            if not self.paused:
                if self.sleep_function:
                    self.idle_id = gobject.idle_add(self.sleep_function)
                if self.running:
                    self.timeout_id = gobject.timeout_add(1000 * self.timeout, self._timeout_cb)

            self.cond.wait()

    def _timeout_cb(self):
        self.cond.acquire()
        self.timeout_id = 0
        self.unlock()

    def _idle_emit_signal(self, symbol_data, q):
        symbol_data.cb(symbol_data.symbol, q, symbol_data.data)


class SymbolGrid(gtk.ScrolledWindow):
    GCONF_PATH = '/apps/bullstock/symbol_grid'

    def __init__(self, hadjustment=None, vadjustment=None):
        super(SymbolGrid, self).__init__(hadjustment, vadjustment)

        #get bullstock-watch portfolio
        self.portfolio = db.store.get(Portfolio, 1)

        self.symbol_monitor = None
        self.treeview = self._build_treeview()
        self.add(self.treeview)

        self._init_config()

        self.connect('delete-event', self._on_delete_event)

    def get_portfolio(self):
        return self.portfolio

    def load_from_db(self):
        if self.symbol_monitor:
            self.symbol_monitor.clear()

        self.symbol_monitor = _SymbolMonitor()
        self.treeview.get_model().clear()

        #load from bullstock-watch portfolio
        for s in self.portfolio.symbols:
            self.append(s)
            self._refresh_item (self._find_iter(s), s)

    def get_selected(self):
        sel = self.treeview.get_selection()
        if sel:
            (model, iter) = sel.get_selected ()
            if iter:
                id = model.get_value(iter, 0)
                s = db.store.get(Symbol, id)
                return s

        return None

    def append(self, symbol):
        store = self.treeview.get_model ()
        i = store.append ()
        store.set_value (i, 0, symbol.id)
        self._fill_iter(i, symbol)

    def update(self, symbol):
        i = self._find_iter(symbol)
        if i:
            self._fill_iter(i, symbol)

    def remove(self, symbol):
        i = self._find_iter(symbol)
        if i:
            self.symbol_monitor.remove(symbol)
            self.treeview.get_model().remove(i)

    def edit(self, symbol):
        i = self._find_iter(symbol)
        path = self.treeview.get_model().get_path (i)
        col = self.treeview.get_column(0)
        self.treeview.set_cursor (path, col, True)

    def get_configure_widget(self, parent):
        dlg = gtk.Dialog(_('Configure Symbol Grid'), parent,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        frame = gtk.Frame(_('Visible Columns'))
        table = gtk.Table(5, 2, True)
        frame.add(table)
        dlg.vbox.pack_start(frame)
        dlg.set_has_separator(False)
        dlg.set_resizable(False)
        dlg.set_size_request(400, -1)

        table.attach(self._create_check_button(_('Symbol'), '/ColSymbol'), 0, 1, 0, 1)
        table.attach(self._create_check_button(_('Name'), '/ColName'), 0, 1, 1, 2)
        table.attach(self._create_check_button(_('Last'), '/ColLast'), 0, 1, 3, 4)
        table.attach(self._create_check_button(_('Percent'), '/ColPercent'), 0, 1, 4, 5)

        table.attach(self._create_check_button(_('Buy Amount'), '/ColBuyAmount'), 1, 2, 0, 1)
        table.attach(self._create_check_button(_('Buy Value'), '/ColBuyValue'), 1, 2, 1, 2)
        table.attach(self._create_check_button(_('Sell Value'), '/ColSellValue'), 1, 2, 2, 3)
        table.attach(self._create_check_button(_('Sell Amount'), '/ColSellAmount'), 1, 2, 3, 4)


        return dlg

    def _check_toggled(self, togglebutton, key):
        self.gconf_client.set_bool(self.GCONF_PATH + key, togglebutton.get_active())

    def _create_check_button(self, caption, gconf_key):
        check = gtk.CheckButton(caption)
        check.set_active(self.gconf_client.get_bool(self.GCONF_PATH + gconf_key))
        check.connect ('toggled', self._check_toggled, gconf_key)
        return check

    def _gconf_value_changed(self, client, connection_id, entry, args):
        self._refresh_config()

    def _init_config(self):
        self.gconf_client = gconf.client_get_default()
        if not self.gconf_client.dir_exists(self.GCONF_PATH):
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColSymbol', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColName', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColLast', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColPercent', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColBuyAmount', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColBuyValue', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColSellValue', True)
            self.gconf_client.set_bool(self.GCONF_PATH + '/ColSellAmount', True)

        self.gconf_client.add_dir(self.GCONF_PATH, gconf.CLIENT_PRELOAD_NONE)
        self.gconf_client.notify_add(self.GCONF_PATH, self._gconf_value_changed)
        self._refresh_config()

    def _set_col_visible(self, col_num, key):
        visible = self.gconf_client.get_bool(self.GCONF_PATH + '/' + key)
        col = self.treeview.get_column(col_num)
        col.set_visible(visible)

    def _refresh_config(self):
        self._set_col_visible(0, 'ColSymbol')
        self._set_col_visible(1, 'ColName')
        self._set_col_visible(2, 'ColLast')
        self._set_col_visible(3, 'ColPercent')
        self._set_col_visible(4, 'ColBuyAmount')
        self._set_col_visible(5, 'ColBuyValue')
        self._set_col_visible(6, 'ColSellValue')
        self._set_col_visible(7, 'ColSellAmount')

    def _fill_iter(self, i, symbol):
        store = self.treeview.get_model ()
        store.set_value (i, 1, symbol.name)
        store.set_value (i, 2, symbol.description)

    def _find_iter(self, symbol):
        iter = self.treeview.get_model().get_iter_first()
        while (iter):
            id = self.treeview.get_model().get_value(iter, 0)
            if id == symbol.id:
                return iter
            iter = self.treeview.get_model().iter_next(iter)


    def _on_delete_event(self, widget, event):
        if self.symbol_monitor:
            self.symbol_monitor.stop()

    def _symbol_updated(self, symbol, q, i):
        if q:
            symbol.refresh(q)
            #update symbol name
            if symbol.description != unicode(q['name']):
                symbol.description = unicode(q['name'])
                db.store.commit()

        store = self.treeview.get_model ()
        if store:
            store.set_value (i, 1, symbol.name)
            if q:
                store.set_value (i, 2, symbol.description)
                store.set_value (i, 3, self._float_format(float(q['last_trade'])))
                store.set_value (i, 4, self._float_to_percent(q['change_percent']))
                store.set_value (i, 5, 0.0)
                if q['bid']:
                    store.set_value (i, 6, self._float_format(q['bid']))
                store.set_value (i, 7, self._float_format (q['ask']))
                store.set_value (i, 8, 0.0)
            else:
                store.set_value (i, 2, 'N/A')
                store.set_value (i, 3, 0.00)
                store.set_value (i, 4, 0.00)
                store.set_value (i, 5, 0.00)
                store.set_value (i, 6, 0.00)
                store.set_value (i, 7, 0.00)
                store.set_value (i, 8, 0.00)

    def _refresh_item (self, i, symbol):
        store = self.treeview.get_model()
        store.set_value (i, 1, symbol.name)
        self.symbol_monitor.append(symbol, self._symbol_updated, i)

    def _on_cell_simbol_start_edit (self, cellrenderertext, editable, path):
        store = self.treeview.get_model ()
        i = store.get_iter (path)
        if i:
            id = store.get_value(i, 0)
            symbol = db.store.get(Symbol, id)
            if symbol:
                self.symbol_monitor.remove(symbol)


    def _on_cell_simbol_edited (self, cellrenderertext, path, new_text):
        store = self.treeview.get_model ()
        i = store.get_iter (path)
        if i:
            id = store.get_value(i, 0)
            symbol = db.store.get(Symbol, id)
            if symbol:
               db.store.commit()
               store.set_value(i, 2, _('Refreshing...'))
               symbol.name = unicode(new_text.upper())
               self._refresh_item (i, symbol)

    def _float_format(self, val):
        return '%5.02f' % float(val)

    def _float_to_percent(self, val):
        return '%5.2f%%' % val

    def _build_treeview(self):
        model = gtk.ListStore(gobject.TYPE_INT,         #symbol.id
                              gobject.TYPE_STRING,      #symbol.name
                              gobject.TYPE_STRING,      #symbol.description
                              gobject.TYPE_STRING,      #symbol.last_value
                              gobject.TYPE_STRING,      #percent
                              gobject.TYPE_STRING,      #sell amount
                              gobject.TYPE_STRING,      #sell value
                              gobject.TYPE_STRING,      #buy value
                              gobject.TYPE_STRING)      #buy amount
        treeview = gtk.TreeView(model)


        #col simbol
        col = gtk.TreeViewColumn (_("Symbol"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        cell.set_property ('editable', True)
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 1)
        cell.connect ('editing-started', self._on_cell_simbol_start_edit)
        cell.connect ('edited', self._on_cell_simbol_edited)

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

gobject.type_register(SymbolGrid)

# vim:ts=4:tw=120:sm:et:si:ai
