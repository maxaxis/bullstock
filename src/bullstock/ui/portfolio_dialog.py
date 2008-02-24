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

class PortfolioDialog(gtk.Dialog):
    def __init__(self, parent):
        super(PortfolioDialog, self).__init__(_('Portfolio'), parent, 
                                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)

        self.set_resizable(False)
        self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)

        self.portfolio_name = gtk.Entry()
        frame = self._create_frame(_('Name'), self.portfolio_name)
        self.vbox.pack_start (frame, False)

        self.portfolio_description = gtk.Entry()
        frame = self._create_frame(_("Description"), self.portfolio_description)
        self.vbox.pack_start (frame, False)

        self.portfolio_trade_cost = gtk.SpinButton(None, 0.0, 2)
        self.portfolio_trade_cost.set_increments(0.5, 1.0)
        #TODO: get max float const
        self.portfolio_trade_cost.set_range(0.0, 100000.0)
        frame = self._create_frame(_("Trade Costs"), self.portfolio_trade_cost)
        self.vbox.pack_start (frame, False)


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

gobject.type_register(PortfolioDialog)

# vim:ts=4:tw=120:sm:et:si:ai
