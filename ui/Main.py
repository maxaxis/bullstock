import gobject
import gtk
from MainWindow import MainWindow

class Application():
    def __init__(self):
        main_win = MainWindow()
        main_win.show_all()
        main_win.connect('delete-event', self.on_delete_window)

    def Run(self):
        gtk.main()

    def on_delete_window(self, widget, event):
        gtk.main_quit()

app = Application()
app.Run()
