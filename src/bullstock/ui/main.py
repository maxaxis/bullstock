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
from decimal import Decimal as Dec

from ui.portfolio_list import PortfolioList
from ui.symbol_grid import SymbolGrid
from ui.portfolio_dialog import PortfolioDialog
from ui.trade_dialog import TradeDialog
from ui.trade_list import TradeList
from model import Portfolio, Symbol
from database import db

class MainWindow(gtk.Window):
    def __init__(self):
        super (MainWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

        self.tips = gtk.Tooltips()

        #symbol grid (Watch List)
        self.symbol_grid = SymbolGrid()
        self.symbol_grid.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.symbol_grid.load_from_db()


        #portfolio list
        self.portfolio_list = PortfolioList()
        self.portfolio_list.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.portfolio_list.load_from_db()
        self.portfolio_list.connect('selection-changed',
                                    self._on_portfolio_changed)

        #trade list
        self.trade_list = TradeList()
        self.symbol_grid.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        #status bar
        self.statusbar = gtk.HBox(False, 0)
        self.statusbar.set_size_request(-1, 15)
        self.progressbar = gtk.ProgressBar()
        self.statusbar.pack_start(self.progressbar, False, True, 0)
        self.statusbar.pack_start(gtk.Label(''), True, True, 0)

        #layout
        main_box = gtk.VBox(False, 5)
        vpaned = gtk.VPaned()

        vbox = gtk.VBox(False, 5)
        toolbar = self._build_watch_toolbar()
        vbox.pack_start(toolbar, False)
        vbox.pack_start(self.symbol_grid, True)
        vpaned.pack1(vbox, True, True)

        vbox = gtk.VBox(False, 5)
        toolbar = self._build_portfolio_toolbar()
        vbox.pack_start(toolbar, False)

        hpaned = gtk.HPaned()
        hpaned.set_position(35)
        vbox.pack_start(hpaned, True)

        hpaned.pack1(self.portfolio_list, True, True)
        hpaned.pack2(self.trade_list, True, True)

        vpaned.pack2(vbox, True, True)

        main_box.pack_start(vpaned, True, True)
        main_box.pack_start(self.statusbar, False, True)

        self.add(main_box)

    def _on_portfolio_changed(self, portfolio):
        p = self.portfolio_list.get_selected()
        if p:
            self.trade_list.refresh(p)

    def _build_toolbar_button (self, stock, tip, cb=None):
        item = gtk.ToolButton(stock)
        item.set_tooltip(self.tips, tip, tip)
        if (cb != None):
            item.connect('clicked', cb, None)

        return item

    def _build_watch_toolbar(self):
        toolbar = gtk.Toolbar ()

        #symbol control
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_PREFERENCES,
                                                   _("Configure Symbol Grid"),
                                                   self._on_configure_symbol_grid),
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

        toolbar.insert (self._build_toolbar_button (gtk.STOCK_UNDO,
                                                    _("Buy selected Symbol"),
                                                    self._on_buy_symbol),
                        -1)

        return toolbar



    def _build_portfolio_toolbar(self):
        toolbar = gtk.Toolbar ()


        #portfolio control
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_ADD,
                                                   _("Add new portfolio"),
                                                   self._on_new_portfolio),
                        -1)
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REMOVE,
                                                   _("Remove selected portfolio"),
                                                   self._on_remove_protfolio),
                        -1)

        toolbar.insert (gtk.SeparatorToolItem(), -1)

        toolbar.insert (self._build_toolbar_button (gtk.STOCK_PREFERENCES, 
                                                   _("Configure portfolio"),
                                                   None),
                        -1)

        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REFRESH, 
                                                   _("Refresh symbol values"),
                                                   None),
                        -1)

        toolbar.insert (gtk.SeparatorToolItem(), -1)

        #symbol control
        toolbar.insert (self._build_toolbar_button (gtk.STOCK_REDO,
                                                    _("Sell selected Symbol"),
                                                    self._on_sell_symbol),
                        -1)
        toolbar.insert (gtk.SeparatorToolItem(), -1)

        return toolbar

    def _on_list_transactions(self, toolbutton, data):
        ##self.details.remove(self.symbol_grid)
        ##self.details.add(self.transaction_list)
        pass
        self.transaction_list.show_all()

    def _on_new_portfolio(self, toolbutton, data):
        dlg = PortfolioDialog(self)
        dlg.show_all()
        ret = dlg.run()
        if ret ==  gtk.RESPONSE_ACCEPT:
            portfolio = Portfolio(unicode(dlg.portfolio_name.get_text()),
                                  Dec(str(dlg.portfolio_trade_cost.get_value())))
            db.store.add(portfolio)
            db.store.commit()
            self.portfolio_list.append(portfolio)

        dlg.destroy()

    def _on_remove_protfolio(self, toolbutton, data):
        p = self.portfolio_list.get_selected()
        if p:
            db.store.remove(p)
            db.store.commit()
            self.portfolio_list.remove(p)

    def _on_configure_symbol_grid(self, toolbutton, data):
        dlg = self.symbol_grid.get_configure_widget(self)
        dlg.show_all()
        dlg.run()
        dlg.destroy()

    def _on_new_symbol(self, toolbutton, data):
        p = self.symbol_grid.get_portfolio()
        if p:
            symbol = Symbol(u'GOOG', u'yahoo')
            db.store.add(symbol)
            p.symbols.add(symbol)
            db.store.commit()
            self.symbol_grid.append(symbol)
            self.symbol_grid.edit(symbol)

    def _on_remove_symbol(self, toolbutton, data):
        s = self.symbol_grid.get_selected()
        if s:
            p = self.portfolio_list.get_selected()
            if p:
                p.symbols.remove(s)
                db.store.commit()
                self.symbol_grid.remove(s)
        else:
            self._show_message(_('You need select a symbol to perform this operation.'))

    def _process_trade(self, trade):
        db.store.add(trade)
        db.store.commit()
        self.trade_list.refresh(trade.portfolio)

    def _create_trade_dialog(self, symbol, type, parent=None):
        #TODO: use cached value
        p = self.portfolio_list.get_selected()
        if type == 'S' and not p:
            return

        if symbol:
            price = symbol.quote['last_trade']
        else:
            price = 0

        dlg = TradeDialog(self, p, symbol, type, price)
        dlg.show_all()
        while (True):
            if dlg.run() == gtk.RESPONSE_OK:
                if not dlg.validate():
                    continue

                trade = dlg.get_trade_object()
                if parent:
                    if parent.amount >= trade.amount:
                        trade.parent_id = parent.id
                    else:
                        continue
                self._process_trade(trade)
                break
            else:
                break

        dlg.destroy()


    def _on_sell_symbol(self, toolbutton, data):
        t = self.trade_list.get_selected()
        if t:
            self._create_trade_dialog(t.symbol, 'S', t)
        else:
            self._show_message(_('You need select a symbol from the portfolio to perform this operation.'))

    def _on_buy_symbol(self, toolbutton, data):
        s = self.symbol_grid.get_selected()
        self._create_trade_dialog(s, 'B')

    def _show_message(self, caption):
        msg = gtk.MessageDialog(self,
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_INFO,
                                gtk.BUTTONS_CLOSE,
                                caption)
        msg.show_all()
        msg.run()
        msg.destroy()


gobject.type_register(MainWindow)

# vim:ts=4:tw=120:sm:et:si:ai
