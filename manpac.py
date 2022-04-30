import os
import sys

# Qt modules
from PyQt5.QtWidgets import (
    QApplication,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QStatusBar,
    QMainWindow,
    QHBoxLayout,
    QLabel
)


class PackageLabel(QLabel):
    """Extends the QLabel class"""

    # Indicates whether a package is selected
    selected = None

    def __init__(self, p, v, window, parent=None):
        super().__init__(parent)
        self.package = p
        self.version = v

        # Determines whether dependency list is loaded for package
        self.loaded = False
        self.dependencies = []
        self.required_by = []

        # Trigger for selecting a package
        self.mouseReleaseEvent = self.show_dependencies

        # Allows for manipulation of widgets in the main window
        self.window = window

    def get_dependencies(self):
        """Gathers dependencies for specific selected package"""

        # Get the output of pacman -Qi {Package Name}
        stream = os.popen('pacman -Qi {}'.format(self.package))
        pkg_info = stream.readlines()

        # Parsing output for dependencies
        for line in pkg_info:
            if 'Depends On' in line:
                d = line

                # More parsing
                i = 0
                for letter in d:

                    if letter == ':':
                        d = line[i + 2:]
                        break
                    else:
                        i += 1

                # Pulls dependencies from output and stores them in class variable
                d_list = [p.strip('\n') for p in d.split(' ')]
                for dep in d_list:
                    if len(dep) >= 2:
                        self.dependencies.append(dep)
                continue

            # Getting "Required By" packages (packages that depend on the selection)
            elif 'Required By' in line:
                r = line
                
                # More parsing
                i = 0
                for letter in r:

                    if letter == ':':
                        r = line[i + 2:]
                        break
                    else:
                        i += 1

                # Pulls package names that require the selected package from output and stores them in class variable
                r_list = [p.strip('\n') for p in r.split(' ')]
                for req in r_list:
                    if len(req) >= 2:
                        self.required_by.append(req)
            else:
                continue
        # Indicates that this package's dependencies and requiring packages variables have been initialized
        self.loaded = True

    def show_dependencies(self, event):
        """Displays the dependencies of selected package in the right pane"""

        # If a package is selected, set that background to NULL before highlighting the new selection
        if PackageLabel.selected:
            PackageLabel.selected.setStyleSheet("")
        self.setStyleSheet("background-color: blue")

        # Updates the status bar
        status = QStatusBar()
        status.showMessage("Selected: {}".format(self.package))
        self.window.setStatusBar(status)

        # Sets currently selected package to variable
        PackageLabel.selected = self

        # Loads dependencies if not already done so
        if not self.loaded:
            self.get_dependencies()

        # Clears previous dependencies listed
        self.window.clear_dependencies()

        # Lists new dependencies from selection
        i = 0
        for d in self.dependencies:
            try:
                self.window.depend_labels[i].setText(d)
                i += 1
            except IndexError:
                break

        # Lists "Required By"
        i = 0
        for r in self.required_by:
            try:
                self.window.req_labels[i].setText(r)
                i += 1
            except IndexError:
                break
       

class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializes a QMainWindow object"""

        super().__init__(parent)

        # Sets the window title
        self.setWindowTitle('manpac')

        # Stores package information
        self.pack_list = []

        # Container for qt labels that contain package information
        self.labels = []

        # Container for qt labels that contain dependency names
        self.depend_labels = []

        # Container for qt labels that contain packages that require the selected package
        self.req_labels = []

        # Loads packages from pacman
        self._get_packages()

        # Initialize the UI components
        self._ui_init()

    def _menu_init(self):
        """Creates the menu for the application"""

        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def _statusbar_init(self):
        """Creates the status bar for the application"""

        status = QStatusBar()
        status.showMessage("Welcome")
        self.setStatusBar(status)

    def _get_packages(self):
        """Returns a list of lists containing package names and version #"""

        stream = os.popen('pacman -Q')
        return self._format_packages(stream.readlines())

    def _format_packages(self, pack_list):
        """Formats the output of pacman -Q into a list of lists stored in a class variable"""

        i = 0
        for line in pack_list:
            for letter in line:
                if letter == ' ':
                    self.pack_list.append([line[:i], line[i:].strip()])
                    i = 0
                    break
                else:
                    i += 1
                    continue

    def _ui_init(self):
        """Initializes the UI of the application"""

        self._menu_init()
        self._statusbar_init()

        # Header widget creation
        self.header_layout = QHBoxLayout()
        self.package_header = QLabel('Package')
        self.depend_header = QLabel('Depends On')
        self.req_header = QLabel('Required By')
        self.header_layout.addWidget(self.package_header)
        self.header_layout.addWidget(self.depend_header)
        self.header_layout.addWidget(self.req_header)
        self.header_widget = QWidget()
        self.header_widget.setLayout(self.header_layout)
    
        # Left column that lists packages
        self.package_area = QScrollArea()
        self.package_area_layout = QVBoxLayout()
        self.widget1 = QWidget()

        # Generates a qt label for each package and adds it to the layout
        for p in self.pack_list:
            label = PackageLabel(p[0], p[1], self)
            label.setText(p[0])
            self.labels.append(label)
            self.package_area_layout.addWidget(label)
    
        # Sets the layout of the left column widget to layout containing all the labels
        self.widget1.setLayout(self.package_area_layout)

        # Sets the ScrollArea() object to contain the widget/layout
        self.package_area.setWidget(self.widget1)

        # Middle column that lists dependencies
        self.depend_area = QScrollArea()
        self.depend_area.setWidgetResizable(True)
        self.depend_area_layout = QVBoxLayout()
        self.depend_widget = QWidget()
    
        # Right column that lists packages that require the selected package
        self.req_area = QScrollArea()
        self.req_area.setWidgetResizable(True)
        self.req_area_layout = QVBoxLayout()
        self.req_widget = QWidget()

        # Generates blank labels to be editable for the dependency and required-by column
        for x in range(50):
            label = QLabel()
            label.setText(' ')
            self.depend_labels.append(label)
            self.depend_area_layout.addWidget(label)
        
        for x in range(50):
            label = QLabel()
            label.setText('')
            self.req_labels.append(label)
            self.req_area_layout.addWidget(label)

        # Sets the layout of the middle column to contain all the blank labels we just created
        self.depend_widget.setLayout(self.depend_area_layout)

        # Sets the layout of the right column to contain all the blank labels we just created
        self.req_widget.setLayout(self.req_area_layout)

        # Sets the widget for the dependency column
        self.depend_area.setWidget(self.depend_widget)

        # Sets the widget for the required by column
        self.req_area.setWidget(self.req_widget)

        # Main horizontal content layout of the app
        self.content_layout = QHBoxLayout()

        # Adds the package column to the content layout
        self.content_layout.addWidget(self.package_area)
        
        # Adds the package and dependency column to the content layout
        self.content_layout.addWidget(self.depend_area)

        # Adds the "required by" column to the contentlayout
        self.content_layout.addWidget(self.req_area)

        # Creates a widget that holds the horizontal content layout
        self.content_widget = QWidget()

        # Adds the content layout to the widget
        self.content_widget.setLayout(self.content_layout)

        # Creates the main layout, and adds the content widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.content_widget)

        # Creates a main (container) widget that houses all other widgets
        main_widget = QWidget()
        main_widget.setGeometry(500, 500, 500, 500)
        main_widget.setLayout(main_layout)

        # Sets the main widget to be centered in the window
        self.setCentralWidget(main_widget)

    def clear_dependencies(self):
        """Clears the right hand column"""

        for label in self.depend_labels:
            label.setText('')
        
        for label in self.req_labels:
            label.setText('')


def main():
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()