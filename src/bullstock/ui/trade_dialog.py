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
from datetime import datetime
from decimal import Decimal as Dec
from gettext import gettext as _

from collector import collect
from model import Symbol, Trade, Portfolio
from database import db


class TradeDialog(gtk.Dialog):
    def __init__(self, parent, portfolio, symbol, type='B', price=0.0, amount=0):
        super (TradeDialog, self).__init__ (_('Trade'), parent)
        hbox = gtk.HBox(False, 5)
        self.set_resizable(False)

        if portfolio and symbol:
            self.valid = True
        else:
            self.valid = False

        self.calendar = gtk.Calendar()
        today = datetime.today()
        self.calendar.select_month(today.month-1, today.year)
        self.calendar.select_day(today.day)
        hbox.pack_start(self.calendar, False)

        vbox = gtk.VBox(False, 5)
        hbox.pack_start(vbox, True)
        self.vbox.pack_start(hbox, True, True, 5)


        #portfolio
        self.portfolio_combo = self._build_portfolio_combo()
        self.portfolio_combo.connect('changed', self._on_portfolio_combo_changed)
        frame = self._create_frame(_('<b>Portfolio</b>'), self.portfolio_combo)
        vbox.pack_start(frame)
        if portfolio:
            self._set_selected_portfolio(portfolio)

        #symbol and type
        hline = gtk.HBox(True, 5)

        self.symbol_combo = self._build_symbol_combo()
        self.symbol_combo.child.connect('focus-out-event', self._on_symbol_combo_lost_focus)
        frame = self._create_frame('<b>Symbol</b>', self.symbol_combo)
        hline.pack_start(frame)

        self.type_label = gtk.Label('')
        frame = self._create_frame('<b>Trade Type</b>', self.type_label)

        hline.pack_start(frame)
        vbox.pack_start(hline)

        #Price and number
        hline = gtk.HBox(True, 5)

        self.price_entry = gtk.SpinButton(None, 0.0, 2)
        self.price_entry.set_increments(0.5, 1.0)
        self.price_entry.set_range(0.0, 100000.0)
        self.price_entry.set_value(price)
        self.price_entry.connect('value-changed', self._values_changed)
        frame = self._create_frame('<b>Price</b>', self.price_entry)

        hline.pack_start(frame)

        self.number_entry = gtk.SpinButton()
        self.number_entry.set_increments(1.0, 10.0)
        self.number_entry.set_range(0.0, 100000.0)
        self.number_entry.set_value(amount)
        self.number_entry.connect('value-changed', self._values_changed)
        frame = self._create_frame('<b>Number of shares</b>', self.number_entry)

        hline.pack_start(frame)
        vbox.pack_start(hline)

        #cost and total
        hline = gtk.HBox(True, 5)

        self.cost_entry = gtk.SpinButton(None, 0.0, 2)
        self.cost_entry.set_increments(0.5, 1.0)
        self.cost_entry.set_range(0.0, 100000.0)
        if portfolio:
           self.cost_entry.set_value(float(portfolio.transaction_cost))
        self.cost_entry.connect('value-changed', self._values_changed)
        frame = self._create_frame('<b>Trade Cost</b>', self.cost_entry)

        hline.pack_start(frame)

        self.total_label = gtk.Label('')
        self.total_label.set_alignment(1.0, 0.5)
        frame = self._create_frame('<b>Total</b>', self.total_label)
        frame.set_shadow_type(gtk.SHADOW_OUT)

        hline.pack_start(frame)
        vbox.pack_start(hline)


        self.set_transaction_type(type)
        self.set_symbol(symbol)
        self._update_sum()

        #Buttons
        self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                         gtk.STOCK_OK, gtk.RESPONSE_OK)

    def set_transaction_type(self, type):
        self.trade_type = type.upper()
        if self.trade_type == 'S':
            self.portfolio_combo.set_sensitive(False)
            self.symbol_combo.set_sensitive(False)
            self.type_label.set_markup(_('<b>Sell</b>'))
        else:
            self.portfolio_combo.set_sensitive(True)
            self.symbol_combo.set_sensitive(True)
            self.type_label.set_markup(_('<b>Buy</b>'))

    def get_transaction_type(self):
        return self.trade_type

    def set_symbol(self, symbol):
        self.symbol = symbol
        if not symbol:
            return

        iter = self.symbol_combo.get_model().get_iter_first()
        while (iter):
            id = self.symbol_combo.get_model().get_value(iter, 0)
            if id == symbol.id:
                self.sumbol_combo.set_active_iter(iter)
                return
            iter = self.treeview.get_model().iter_next(iter)

        #if not in the list append this
        model = self.symbol_combo.get_model()
        i = model.append()
        model.set_value(i, 0, symbol.id)
        model.set_value(i, 1, symbol.name)
        self.symbol_combo.set_active_iter(i)

    def get_symbol(self):
        i = self.symbol_combo.get_active_iter()
        if i:
            id = self.symbol_combo.get_model().get_value(i, 0)
            s = db.store.get(Symbol, id)
            return s
        else:
            return Symbol(unicode(self.symbol_combo.child.get_text()), u'yahoo')

    def validate(self):
        i = self.portfolio_combo.get_active_iter()
        if not i:
            self._show_message(_('A portfolio need be selected'))
            return False

        if not self.symbol:
            self._show_message(_('A valid symbol is necessary'))
            return False

        qnt = self.number_entry.get_value()
        if qnt <= 0:
            self._show_message(_('A value big then 0 is necessary on number of shares.'))
            return False

        self._update_sum()
        return self.valid

    def get_trade_object(self):
        (year, month, day) = self.calendar.get_date()
        return Trade(unicode(self.get_transaction_type()),
                     self.symbol,
                     self._get_selected_portfolio(),
                     self.number_entry.get_value(),
                     Dec(str(self.price_entry.get_value())),
                     Dec(str(self.cost_entry.get_value())),
                     datetime(year, month, day))

    def _on_symbol_combo_lost_focus(self, widget, event):
        try:
            quote = collect.get_quote(u'yahoo', unicode(widget.get_text()))
            self.symbol = Symbol(unicode(widget.get_text()), u'yahoo', quote)
            self.valid = True
            self.price_entry.set_text(str(quote['last_trade']))
            self._update_sum()
        except:
            self._show_message('Invalid symbol name')
            self.valid = False
            return False

        return False

    def _on_portfolio_combo_changed(self, combo):
        p = self._get_selected_portfolio()
        if p:
            self._load_symbols(p)
            self.cost_entry.set_value(p.transaction_cost)

    def _set_selected_portfolio(self, p):
        iter = self.portfolio_combo.get_model().get_iter_first()
        while (iter):
            id = self.portfolio_combo.get_model().get_value(iter, 0)
            if id == p.id:
                self.portfolio_combo.set_active_iter(iter)
                return
            iter = self.treeview.get_model().iter_next(iter)

    def _get_selected_portfolio(self):
        i = self.portfolio_combo.get_active_iter()
        if i:
            id = self.portfolio_combo.get_model().get_value(i, 0)
            p = db.store.get(Portfolio, id)
            return p

        return None

    def _load_symbols(self, p):
        for s in p.symbols:
            i = model.append()
            model.set_value(i, 0, s.id)
            model.set_value(i, 1, s.name)

    def _build_symbol_combo(self):
        model = gtk.ListStore(gobject.TYPE_INT,
                              gobject.TYPE_STRING)
        combo = gtk.ComboBoxEntry(model, 1)
        return combo


    def _build_portfolio_combo(self):
        model = gtk.ListStore(gobject.TYPE_INT,
                              gobject.TYPE_STRING)
        combo = gtk.ComboBox(model)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 1)

        for p in db.store.find(Portfolio, Portfolio.id != 1):
            i = model.append()
            model.set_value(i, 0, p.id)
            model.set_value(i, 1, p.name)

        return combo

    def _update_sum(self):
        price = self.price_entry.get_value()
        amount = self.number_entry.get_value()
        cost = self.cost_entry.get_value()

        if self.get_transaction_type() == 'S':
            cost = -cost

        total = price * amount + cost

        self.total_label.set_markup("%5.2f" % total)

    def _values_changed(self, editable):
        self._update_sum()

    def _create_frame(self, label, child):
        frame = gtk.Frame('')
        lbl = frame.get_label_widget()
        lbl.set_markup(label)

        alg = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
        alg.set_padding(0, 0, 12, 0)
        alg.add(child)

        frame.add(alg)
        frame.set_shadow_type(gtk.SHADOW_NONE)

        return frame

    def _show_message(self, caption):
        msg = gtk.MessageDialog(self,
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_INFO,
                                gtk.BUTTONS_CLOSE,
                                caption)
        msg.show_all()
        msg.run()
        msg.destroy()

gobject.type_register(TradeDialog)

# vim:ts=4:tw=120:sm:et:si:ai
