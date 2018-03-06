# Allows for import of user.py
from inspect import getsourcefile
import os.path as path, sys
cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, cur_dir[:cur_dir.rfind(path.sep)])

from PyQt5.QtWidgets import (QMainWindow, QAction, QWidget, QVBoxLayout,
    QTabWidget, QTableWidgetItem)
from PyQt5 import QtCore

from tabs import SongUI, CreateQueueUI, CurrentQueueUI
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
        self.user = user

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = SongUI(self, user)
        self.tab2 = CreateQueueUI(self, user)
        self.tab3 = CurrentQueueUI(self, user) 
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, 'Playlist Songs')
        self.tabs.addTab(self.tab2, 'Queue Maker')
        self.tabs.addTab(self.tab3, 'Current Queue')

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Add currently selected songs in playlist songs tab to queue
        self.tab1.add_songs.clicked.connect(self.add_to_queue)

        # Create queue with currently shown songs
        self.tab2.create_songs.clicked.connect(self.create_queue)

    def add_to_queue(self):
        """
        Creates the queue based on the songs in the queue list maker
        """
        # Current row count
        row_count = self.tab2.queue_list.rowCount()
        # Rows selected to add
        selected_rows = [x.row() for x in self.tab1.songs_table.selectedIndexes()]
        # Iterate through each row of QTableWidget in Queue Maker
        for n, row in enumerate(selected_rows):
            # Skip song if no ID
            if not self.tab1.songs_table.item(row, 2).text():
                continue

            # Create row
            self.tab2.queue_list.insertRow(row_count + n)

            # Add song
            song = QTableWidgetItem(self.tab1.songs_table.item(row, 0))
            # Remove ability to select it
            song.setFlags(QtCore.Qt.ItemIsEnabled)
            song.setFlags(QtCore.Qt.ItemIsSelectable)
            self.tab2.queue_list.setItem(row_count + n, 0, song)

            # Add artist(s)
            artist = QTableWidgetItem(self.tab1.songs_table.item(row, 1).text())
            # Remove the ability to select it
            artist.setFlags(QtCore.Qt.ItemIsEnabled)
            artist.setFlags(QtCore.Qt.ItemIsSelectable)
            self.tab2.queue_list.setItem(row_count + n, 1, artist)

            # Hidden column with song IDs
            song_id = QTableWidgetItem(self.tab1.songs_table.item(row, 2).text())
            self.tab2.queue_list.setItem(row_count + n, 2, song_id)

    def create_queue(self):
        """
        Creates a queue of the songs in the QTableWidget under Queue Maker
        """
        # Reset the data by removing old songs and whatnot
        for _ in range(self.tab3.current_queue.rowCount()):
            self.tab3.current_queue.removeRow(0)
        self.tab3.current_queue.verticalHeader().setVisible(False)

        song_ids = []
        for row in range(self.tab2.queue_list.rowCount()):
            # Create the row
            self.tab3.current_queue.insertRow(row)

            # Add song name
            song = QTableWidgetItem(self.tab2.queue_list.item(row, 0).text())
            song.setFlags(QtCore.Qt.ItemIsEnabled)
            song.setFlags(QtCore.Qt.ItemIsSelectable)
            self.tab3.current_queue.setItem(row, 0, song)

            # Add artist(s)
            artist = QTableWidgetItem(self.tab2.queue_list.item(row, 1).text())
            artist.setFlags(QtCore.Qt.ItemIsEnabled)
            artist.setFlags(QtCore.Qt.ItemIsSelectable)
            self.tab3.current_queue.setItem(row, 1, artist)

            # Hidden column with song IDs
            song_id = QTableWidgetItem(self.tab2.queue_list.item(row, 2).text())
            self.tab3.current_queue.setItem(row, 2, song_id)
            # Record IDs for creating queue
            song_ids.append(song_id.text())

        # Create queue
        self.user.create_queue(song_ids)
