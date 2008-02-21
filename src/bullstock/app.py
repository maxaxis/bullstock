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

import sys
import gtk

from configuration import config
from collector import collect
from database import db

from ui.main import MainWindow

class Application():
    def __init__(self):
        main_win = MainWindow()
        main_win.show_all()
        main_win.connect('delete-event', self.on_delete_window)

    def run(self):
        gtk.main()

    def on_delete_window(self, widget, event):
        gtk.main_quit()

application = Application()

def main(*args, **kwargs):
    application.run()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# vim:ts=4:tw=120:sm:et:si:ai
