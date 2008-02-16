import gobject
import gtk

from gettext import gettext as _

class StockGridWindow(gtk.Window):
    def __init__(self):
        super (StockGridWindow, self).__init__ (gtk.WINDOW_TOPLEVEL)

        vbox = gtk.VBox (False, 5)

        self.grid = self.build_grid ()
        scroll = gtk.ScrolledWindow (None, None)
        scroll.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add (self.grid)

        hbox = gtk.HBox (False, 5)
        self.wallet_combo = gtk.ComboBox()
        hbox.pack_start (self.wallet_combo)

        btn = gtk.Button ()
        img = gtk.Image ()
        img.set_from_stock (gtk.STOCK_EDIT, gtk.ICON_SIZE_SMALL_TOOLBAR)
        btn.set_image (img)
        hbox.pack_start (btn, False)

        btn = gtk.Button ()
        img = gtk.Image ()
        img.set_from_stock (gtk.STOCK_NEW, gtk.ICON_SIZE_SMALL_TOOLBAR)
        btn.set_image (img)
        hbox.pack_start (btn, False)

        btn = gtk.Button ()
        img = gtk.Image ()
        img.set_from_stock (gtk.STOCK_DELETE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        btn.set_image (img)
        hbox.pack_start (btn, False)

        vbox.pack_start (hbox, False)
        vbox.pack_start (scroll)

        hbox = gtk.HBox (False, 5)

        btn = gtk.Button ()
        img = gtk.Image ()
        img.set_from_stock (gtk.STOCK_NEW, gtk.ICON_SIZE_SMALL_TOOLBAR)
        btn.set_image (img)
        hbox.pack_start (btn, False)

        btn = gtk.Button ()
        img = gtk.Image ()
        img.set_from_stock (gtk.STOCK_DELETE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        btn.set_image (img)
        hbox.pack_start (btn, False)

        vbox.pack_start (hbox, False)

        self.add (vbox)

    def build_grid (self):

        model = gtk.ListStore (gobject.TYPE_STRING, gobject.TYPE_DOUBLE, gobject.TYPE_DOUBLE, gobject.TYPE_STRING, gobject.TYPE_DOUBLE, gobject.TYPE_DOUBLE, gobject.TYPE_STRING)
        treeview = gtk.TreeView (model)


        #col name
        col = gtk.TreeViewColumn (_("Stock"))
        col.set_min_width (150)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 0)

        #col value
        col = gtk.TreeViewColumn (_("Last ($)"))
        col.set_min_width (100)
        treeview.append_column (col)
        cell = gtk.CellRendererText ()
        col.pack_start (cell, False)
        col.add_attribute (cell, 'text', 1)

        #col %
        col = gtk.TreeViewColumn (_("Day  (%)"))
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



gobject.type_register(StockGridWindow)
