# Allows for import of user.py
from inspect import getsourcefile
import os.path as path, sys
cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, cur_dir[:cur_dir.rfind(path.sep)])

from PyQt5.QtWidgets import (QMainWindow, QAction, QWidget, QVBoxLayout,
    QTabWidget, )

from tabs import SongUI, QueueUI
from user import User
sys.path.pop(0)


class Window(QMainWindow):

    def __init__(self, client):
        """
        Main Window of GUI.

        Parameters:
        client - The Client object with the access token and everything
        """
        super().__init__()

        # Get the backend data
        self.client = client
        self.user = User(self.client.access_token, self.client.token_birth)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Spearch')
        self.resize(600, 400)

        self.menu = self.menuBar()
        file_menu = self.menu.addMenu('&File')
        file_menu.addAction(QAction('Hello', self))

        self.tabs = Tabs(self, self.user)
        self.setCentralWidget(self.tabs)


class Tabs(QWidget):

    def __init__(self, parent, user):
        """
        Widget that creates each tab and pull the layouts for each one from
        their respective classes.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.sui = SongUI(self, user)
        self.qui = QueueUI(self, user)
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.sui, 'Playlist Songs')
        self.tabs.addTab(self.qui, 'Queue Maker')

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
