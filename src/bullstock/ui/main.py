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

from ui.stockgrid import StockGridWindow

from gettext import gettext as _

class MainWindow(gtk.Window):
    def __init__(self):
        super (MainWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

        menu = '''
            <ui>
             <menubar name="Menubar">
              <menu action="Menu">
               <menu action="Stock">
                <menuitem action="Grid"/>
               </menu>
               <separator/>
               <menuitem action="Quit"/>
              </menu>
             </menubar>
            </ui>
        '''
        actions = [
            ('Menu', None, _("File")),
            ('Stock', None, _("_Stock")),
            ('Grid', gtk.STOCK_INDEX, _("Grid"), None, _("Stock Grid"), self.on_menu_grid),
            ('Quit', gtk.STOCK_QUIT, _("Quit"), None, _("Close application"), self.on_menu_quit)]

        ag =  gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)

        vbox = gtk.VBox(False, 5)
        menu = self.manager.get_widget('/Menubar')
        vbox.pack_start (menu, False)
        self.add (vbox)
        self.set_size_request (800, 480)

    def on_menu_grid(self, data):
        grid = StockGridWindow (self)
        grid.show_all ()
        grid.set_size_request (500, 300)

    def on_menu_quit(self, data):
        None

gobject.type_register(MainWindow)

# vim:ts=4:tw=120:sm:et:si:ai
