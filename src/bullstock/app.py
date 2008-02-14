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

import sys

from config import configuration
from collector import Collector
from utils import s2d

def main(*args, **kwargs):
    collector = Collector()
    collector.select_datasource("yahoo")

    print collector.get_quote("VALE5.SA")
    print collector.get_table("VALE5.SA") #full
    print collector.get_table("VALE5.SA", start=s2d("2007-01-01"), end=s2d("2008-01-01")) #1y

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# vim:ts=4:tw=120:sm:et:si:ai
