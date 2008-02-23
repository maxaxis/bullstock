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

from model import Symbol, Trade

class TradeDialog(gtk.Dialog):
    def __init__(self, parent, portfolio, symbol, type='B', price=0.0, amount=0):
        super (TradeDialog, self).__init__ (_('Trade'), parent)
        hbox = gtk.HBox(False, 5)
        self.set_resizable(False)
        self.potfolio = portfolio

        self.calendar = gtk.Calendar()
        hbox.pack_start(self.calendar, False)

        vbox = gtk.VBox(True, 5)
        hbox.pack_start(vbox, True)
        self.vbox.pack_start(hbox, True, True, 5)

        #symbol and type
        hline = gtk.HBox(True, 5)

        self.symbol_entry = gtk.Entry()
        self.symbol_entry.set_sensitive(False)
        frame = self._create_frame('<b>Symbol</b>', self.symbol_entry)

        hline.pack_start(frame)

        self.type_combo = gtk.combo_box_new_text()
        self.type_combo.insert_text(0, _('Sell'))
        self.type_combo.insert_text(1, _('Buy'))
        frame = self._create_frame('<b>Trade Type</b>', self.type_combo)

        hline.pack_start(frame)
        vbox.pack_start(hline)

        #Price and number
        hline = gtk.HBox(True, 5)

        self.price_entry = gtk.SpinButton(None, 0.0, 2)
        self.price_entry.set_increments(0.5, 1.0)
        self.price_entry.set_range(0.0, 100000.0)
        self.price_entry.set_value(price)
        self.price_entry.connect('changed', self._values_changed)
        frame = self._create_frame('<b>Price</b>', self.price_entry)

        hline.pack_start(frame)

        self.number_entry = gtk.SpinButton()
        self.number_entry.set_increments(1.0, 10.0)
        self.number_entry.set_range(0.0, 100000.0)
        self.number_entry.set_value(amount)
        self.number_entry.connect('changed', self._values_changed)
        frame = self._create_frame('<b>Number of shares</b>', self.number_entry)

        hline.pack_start(frame)
        vbox.pack_start(hline)

        #cost and total
        hline = gtk.HBox(True, 5)

        self.cost_entry = gtk.SpinButton(None, 0.0, 2)
        self.cost_entry.set_increments(0.5, 1.0)
        self.cost_entry.set_range(0.0, 100000.0)
        self.cost_entry.set_value(float(portfolio.transaction_cost))
        self.cost_entry.connect('changed', self._values_changed)
        frame = self._create_frame('<b>Trade Cost</b>', self.cost_entry)

        hline.pack_start(frame)

        self.total_label = gtk.Label('')
        self.total_label.set_alignment(1.0, 0.5)
        frame = self._create_frame('<b>Total</b>', self.total_label)
        frame.set_shadow_type(gtk.SHADOW_OUT)

        hline.pack_start(frame)
        vbox.pack_start(hline)


        self.set_transaction_type(type)
        if symbol:
            self.set_symbol(symbol)
        self._update_sum()

        #Buttons
        self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                         gtk.STOCK_OK, gtk.RESPONSE_OK)

    def set_transaction_type(self, type):
        if type.upper() == 'S':
            self.type_combo.set_active(0)
        else:
            self.type_combo.set_active(1)

    def get_transaction_type(self):
        if self.type_combo.get_active() == 0:
            return 'S'
        else:
            return 'B'

    def set_symbol(self, symbol):
        self.symbol = symbol
        self.symbol_entry.set_text(symbol.name)
        #TODO: update price

    def get_symbol(self):
        return self.symbol

    def valid(self):
        if self.get_transaction_type() == 'B':
            return True
        if self.get_transaction_type() == 'S':
            if self.symbol.amount >= self.number_entry.get_value():
                return True
            else:
                msg = gtk.MessageDialog(self,
                                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_INFO,
                                        gtk.BUTTONS_CLOSE,
                                        _('Current amount is not avalible to sell.'))
                msg.show_all()
                msg.run()
                msg.destroy()

        return False

    def get_trade_object(self):
        return Trade(unicode(self.get_transaction_type()),
                     self.symbol,
                     self.portfolio,
                     self.number_entry.get_value(),
                     Dec(str(self.price_entry.get_value())),
                     Dec(str(self.cost_entry.get_value())),
                     datetime(self.calendar.get_date()))

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


gobject.type_register(TradeDialog)

# vim:ts=4:tw=120:sm:et:si:ai
