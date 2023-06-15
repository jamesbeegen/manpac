	

import gi
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, package):
        super().__init__()
        self.package = package
        self.add(Gtk.Label(label=package))

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hello World")

        # Obtain list of packages
        self.packages = []
        self.get_packages()

        # Main box
        self.box = Gtk.Box(spacing=3)
        self.add(self.box)

        # "Packages Column"
        self.packages_box = Gtk.VBox()
        self.package_label = Gtk.Label(label="Package")
        self.package_list = Gtk.ListBox()

        for package in range(1000):
            print(package)
            self.package_list.add(ListBoxRowWithData(package))

        self.packages_box.pack_start(self.package_label, True, True, 0)
        #self.packages_box.pack_start(self.package_list, True, True, 0)
        self.box.pack_start(self.packages_box, True, True, 0)
        self.scroll1 = Gtk.ScrolledWindow()
        self.scroll1.add_with_viewport(self.packages_box)
        self.box.add(self.scroll1)


        # "Depends On" Column
        self.depends_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.depends_label = Gtk.Label(label="Depends On")
        self.depends_list = Gtk.ListBox()
        self.depends_box.pack_start(self.depends_label, True, True, 0)
        self.depends_box.pack_start(self.depends_list, True, True, 0)
        self.box.pack_start(self.depends_box, True, True, 0)

        # "Required By" Label        
        self.requiredBy_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.requiredBy_label = Gtk.Label(label="Required By")
        self.requiredBy_list = Gtk.ListBox()
        self.requiredBy_box.pack_start(self.requiredBy_label, True, True, 0)
        self.requiredBy_box.pack_start(self.requiredBy_list, True, True, 0)
        self.box.pack_start(self.requiredBy_box, True, True, 0)


    def get_packages(self):
        """Returns a list of lists containing package names and version #"""

        stream = os.popen('pacman -Q')
        return self.format_packages(stream.readlines())


    def format_packages(self, pack_list):
        """Formats the output of pacman -Q into a list of lists stored in a class variable"""

        i = 0
        for line in pack_list:
            for letter in line:
                if letter == ' ':
                    self.packages.append([line[:i], line[i:].strip()])
                    i = 0
                    break
                else:
                    i += 1
                    continue



win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
