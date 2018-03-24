# Allows for import of user.py
from inspect import getsourcefile
import os.path as path, sys
cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, cur_dir[:cur_dir.rfind(path.sep)])

from functools import partial
from time import sleep

from PyQt5.QtWidgets import (QMainWindow, QAction, QWidget, QVBoxLayout,
    QTabWidget, QTableWidgetItem, qApp, QDialog, QMenu)
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from tabs import SongUI, CreateQueueUI, CurrentQueueUI, FilterUI
from popups import Login
from user import User
sys.path.pop(0)


class Window(QMainWindow):
    NEW_USER_EXIT_CODE = 322
    BOLD_FONT = QFont()
    BOLD_FONT.setBold(True)

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
        self.init_menu()

    def init_ui(self):
        self.setWindowTitle('Spearch')
        self.resize(600, 400)

        self.tabs = Tabs(self, self.user)
        self.setCentralWidget(self.tabs)

    def init_menu(self):
        # Init menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu('File')
        edit_menu = self.menu.addMenu('Edit')

        ### FILE ###
        # New user
        new_user = QAction('New User', self)
        new_user.setShortcut('Ctrl+N')
        new_user.setStatusTip('Sign in with new user')
        new_user.triggered.connect(self._relogin)

        # Quit
        quit_app = QAction('Quit', self)
        quit_app.setShortcut('Ctrl+Q')
        quit_app.setStatusTip('Quit Application')
        quit_app.triggered.connect(qApp.quit)

        # Add to File
        file_menu.addAction(new_user)
        file_menu.addSeparator()
        file_menu.addAction(quit_app)

        ### EDIT ###
        # Choose available devices
        self.avail = QMenu('Choose Different Device', self)
        self.avail.setStatusTip('Choose a different available device')
        self._reset_avail_devices()

        # Check for new available devices (submenu of self.avail)
        check_avail = QAction('Check Available Devices', self)
        check_avail.setShortcut('Ctrl+D')
        check_avail.setStatusTip('Check for new available devices')
        check_avail.triggered.connect(self._reset_avail_devices)

        # Add to Edit
        edit_menu.addMenu(self.avail)
        edit_menu.addAction(check_avail)

    def _reset_avail_devices(self, device_id=None):
        """
        Resets the available devices with the updated ones.

        Parameters:
        device_id - (default None) If given, this device will automatically be
                    chosen to be bold (i.e. selected). When initialized, the
                    chosen device is determined by the is_active data, for the
                    rest, the device is known, so it's just pass because the
                    is_active can be wrong (due to polling too quickly maybe?)
        """
        # Clears menu
        self.avail.clear()

        # Add each one
        for device_info in self.user.get_available_devices():
            name = device_info['name']

            device = QAction(name, self)
            # Bold the chosen device
            if (device_info['is_active'] and device_id is None) or \
               (device_info['id'] == device_id):
                device.setFont(self.BOLD_FONT)

            # Use functools.partial cause otherwise with just lambda, the
            # closure messing it up and only uses last instance of device_info
            device.triggered.connect(partial(
                self._change_device, device_info['id']))
            # Add to submenu
            self.avail.addAction(device)

    def _change_device(self, device_id):
        """
        Changes the device by using the User change_device method and then
        resetting the available devices.
        """
        self.user.change_device(device_id)
        self._reset_avail_devices(device_id)

    def _relogin(self):
        """
        Brings up new window to log in as a new user
        """
        # New login window
        login = Login()
        result = login.exec_()

        if result == QDialog.Accepted:
            self.client = login.client
            # Exit current app with code that tells main loop to repeat
            qApp.exit(self.NEW_USER_EXIT_CODE)


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

        self.pl_tab = SongUI(self, user)
        self.filt_tab = FilterUI(self, user)
        self.createq_tab = CreateQueueUI(self, user)
        self.curq_tab = CurrentQueueUI(self, user)

        # Add tabs
        self.tabs.addTab(self.pl_tab, 'Playlist Songs')
        self.tabs.addTab(self.filt_tab, 'Filter Playlists')
        self.tabs.addTab(self.createq_tab, 'Queue Maker')
        self.tabs.addTab(self.curq_tab, 'Current Queue')

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Add currently selected songs in playlist songs tab to queue
        self.pl_tab.add_songs_button.clicked.connect(lambda:
            self._add_to_queue(self.pl_tab.songs_table, True))
        self.filt_tab.add_songs_button.clicked.connect(lambda:
            self._add_to_queue(self.filt_tab.songs_table, False))

        # Create queue with currently shown songs
        self.createq_tab.create_songs.clicked.connect(self._create_queue)

    def _add_to_queue(self, songs_table, selected):
        """
        Creates the queue based on the songs in the queue list maker. The songs
        added from the playlist tab are only the selected songs whereas the
        songs added from the filter tab are all of them as determined by
        the `selected` boolean.
        """
        # Current row count
        row_count = self.createq_tab.queue_list.rowCount()
        # Rows selected to add
        if selected:
            row_nums = [x.row() for x in songs_table.selectedIndexes()]
        else:
            row_nums = range(songs_table.rowCount())

        num_skipped = 0
        # Iterate through each row of QTableWidget in Queue Maker
        for n, row in enumerate(row_nums):
            # Skip song if no ID
            if not songs_table.item(row, 2).text():
                num_skipped += 1
                continue

            # Current row index
            ind = row_count + n - num_skipped

            # Create row
            self.createq_tab.queue_list.insertRow(ind)

            # Add song
            song = QTableWidgetItem(songs_table.item(row, 0))
            # Remove ability to select it
            song.setFlags(QtCore.Qt.ItemIsEnabled)
            song.setFlags(QtCore.Qt.ItemIsSelectable)
            self.createq_tab.queue_list.setItem(ind, 0, song)

            # Add artist(s)
            artist = QTableWidgetItem(songs_table.item(row, 1).text())
            # Remove the ability to select it
            artist.setFlags(QtCore.Qt.ItemIsEnabled)
            artist.setFlags(QtCore.Qt.ItemIsSelectable)
            self.createq_tab.queue_list.setItem(ind, 1, artist)

            # Hidden column with song IDs
            song_id = QTableWidgetItem(songs_table.item(row, 2).text())
            self.createq_tab.queue_list.setItem(ind, 2, song_id)

    def _create_queue(self):
        """
        Creates a queue of the songs in the QTableWidget under Queue Maker
        """
        # Reset the data by removing old songs and whatnot
        for _ in range(self.curq_tab.current_queue.rowCount()):
            self.curq_tab.current_queue.removeRow(0)
        self.curq_tab.current_queue.verticalHeader().setVisible(False)

        song_ids = []
        for row in range(self.createq_tab.queue_list.rowCount()):
            # Create the row
            self.curq_tab.current_queue.insertRow(row)

            # Add song name
            song = QTableWidgetItem(self.createq_tab.queue_list.item(row, 0).text())
            song.setFlags(QtCore.Qt.ItemIsEnabled)
            song.setFlags(QtCore.Qt.ItemIsSelectable)
            self.curq_tab.current_queue.setItem(row, 0, song)

            # Add artist(s)
            artist = QTableWidgetItem(self.createq_tab.queue_list.item(row, 1).text())
            artist.setFlags(QtCore.Qt.ItemIsEnabled)
            artist.setFlags(QtCore.Qt.ItemIsSelectable)
            self.curq_tab.current_queue.setItem(row, 1, artist)

            # Hidden column with song IDs
            song_id = QTableWidgetItem(self.createq_tab.queue_list.item(row, 2).text())
            self.curq_tab.current_queue.setItem(row, 2, song_id)
            # Record IDs for creating queue
            song_ids.append(song_id.text())

        # Create queue
        self.user.create_queue(song_ids)
