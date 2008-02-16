import gobject
import gtk

from StockGridWindow import StockGridWindow

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
        grid = StockGridWindow ()
        grid.show_all ()

    def on_menu_quit(self, data):
        None

gobject.type_register(MainWindow)
