# Allows for import of user.py
from inspect import getsourcefile
import os.path as path, sys

cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, cur_dir[: cur_dir.rfind(path.sep)])

from functools import partial

from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTableWidgetItem,
    qApp,
    QDialog,
    QMenu,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from tabs import (
    PlaylistSongsUI,
    AdvFilterPlaylistsUI,
    SimpleFilterPlaylistUI,
    QueueMakerUI,
)
from popups import Login
from user import User
from style import TabStyle, BG_COLOR

sys.path.pop(0)


class Window(QMainWindow):
    NEW_USER_EXIT_CODE = 322
    BOLD_FONT = QFont()
    BOLD_FONT.setBold(True)
    NORMAL_FONT = QFont()

    def __init__(self, client, max_height, max_width):
        """
        Main Window of GUI.

        Parameters:
        client - The Client object with the access token and everything
        """
        super().__init__()

        # Get the backend data
        self.client = client
        self.user = User(self.client.access_token, self.client.token_birth)

        self.init_ui(max_height, max_width)
        self.init_menu()

    def init_ui(self, max_height, max_width):
        self.setWindowTitle("Spearch")

        self.tabs = Tabs(self, self.user, max_height, max_width)
        self.setCentralWidget(self.tabs)

        self.setStyleSheet("QMainWindow {{background-color: {}}}".format(BG_COLOR))

    def init_menu(self):
        # Init menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")
        edit_menu = self.menu.addMenu("Edit")

        ### FILE ###
        # New user
        new_user = QAction("New User", self)
        new_user.setShortcut("Ctrl+N")
        new_user.setStatusTip("Sign in with new user")
        new_user.triggered.connect(self._relogin)

        # Quit
        quit_app = QAction("Quit", self)
        quit_app.setShortcut("Ctrl+Q")
        quit_app.setStatusTip("Quit Application")
        quit_app.triggered.connect(qApp.quit)

        # Add to File
        file_menu.addAction(new_user)
        file_menu.addSeparator()
        file_menu.addAction(quit_app)

        ### EDIT ###
        # Choose available devices
        self.avail = QMenu("Choose Different Device", self)
        self.avail.setStatusTip("Choose a different available device")
        self._reset_avail_devices()

        # Check for new available devices (submenu of self.avail)
        check_avail = QAction("Check Available Devices", self)
        check_avail.setShortcut("Ctrl+D")
        check_avail.setStatusTip("Check for new available devices")
        check_avail.triggered.connect(self._reset_avail_devices)

        # Change from simple to advanced mode for Filter Playlist tab
        toggle_filter = QMenu("Toggle Filter Playlists tab", self)
        toggle_filter.setStatusTip(
            "Toggle between simple and advanced mode" + " for the Filter Playlists tab"
        )
        # The two options in the submenu
        self.simple_filter = QAction("Simple", self)
        # Start with simple filter selected
        self.simple_filter.setFont(self.BOLD_FONT)
        self.advanced_filter = QAction("Advanced", self)
        # Do the changing when clicked
        self.simple_filter.triggered.connect(partial(self._toggle_filter, "simple"))
        self.advanced_filter.triggered.connect(partial(self._toggle_filter, "advanced"))
        toggle_filter.addAction(self.simple_filter)
        toggle_filter.addAction(self.advanced_filter)

        # Add to Edit
        edit_menu.addMenu(self.avail)
        edit_menu.addAction(check_avail)
        edit_menu.addSeparator()
        edit_menu.addMenu(toggle_filter)

    def _toggle_filter(self, ui_to_toggle):
        """
        Toggle between the advanced and simple version for filtering playlists

        Parameters:
        ui_to_toggle - Either 'simple' or 'advanced'. 'simple' will bold 
                       'Simple' in the menu and change the second tab to the
                       simplified version and vis versa
        """
        if ui_to_toggle == "simple":
            # Toggle the bold fonts
            self.simple_filter.setFont(self.BOLD_FONT)
            self.advanced_filter.setFont(self.NORMAL_FONT)
            # Remove old tab and insert new one
            self.tabs.tabs.removeTab(1)
            self.tabs.tabs.insertTab(1, self.tabs.simp_filt_tab, "Filter Playlists")
        elif ui_to_toggle == "advanced":
            # Toggle the bold fonts
            self.simple_filter.setFont(self.NORMAL_FONT)
            self.advanced_filter.setFont(self.BOLD_FONT)
            # Remove old tab and insert new one
            self.tabs.tabs.removeTab(1)
            self.tabs.tabs.insertTab(1, self.tabs.adv_filt_tab, "Filter Playlists")
        # Set back to current tab (otherwise moves to next tab)
        self.tabs.tabs.setCurrentIndex(1)

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
            name = device_info["name"]

            device = QAction(name, self)
            # Bold the chosen device
            if (device_info["is_active"] and device_id is None) or (
                device_info["id"] == device_id
            ):
                device.setFont(self.BOLD_FONT)

            # Use functools.partial cause otherwise with just lambda, the
            # closure messing it up and only uses last instance of device_info
            device.triggered.connect(partial(self._change_device, device_info["id"]))
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
    def __init__(self, parent, user, max_height, max_width):
        """
        Widget that creates each tab and pull the layouts for each one from
        their respective classes.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.user = user

        # Initialize tab screen
        self.tabs = QTabWidget()

        self.pl_tab = PlaylistSongsUI(None, user)
        self.simp_filt_tab = SimpleFilterPlaylistUI(None, user, max_height, max_width)
        self.adv_filt_tab = AdvFilterPlaylistsUI(None, user, max_height, max_width)
        self.createq_tab = QueueMakerUI(None, user)

        # Add tabs
        self.tabs.addTab(self.pl_tab, "Playlist Songs")
        self.tabs.addTab(self.simp_filt_tab, "Filter Playlists")
        self.tabs.addTab(self.createq_tab, "Queue Maker")

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Adds selected songs from Playlist tab to the Current Queue tab
        self.pl_tab.add_songs_button.clicked.connect(
            lambda: self.createq_tab.queue_list.add_songs(
                self.pl_tab.songs_table, False, True
            )
        )
        # Adds songs from Simple/Advanced Filter tab to Current Queue tab
        self.simp_filt_tab.add_songs_button.clicked.connect(
            lambda: self.createq_tab.queue_list.add_songs(
                self.simp_filt_tab.songs_table, False, False
            )
        )
        self.adv_filt_tab.add_songs_button.clicked.connect(
            lambda: self.createq_tab.queue_list.add_songs(
                self.adv_filt_tab.songs_table, False, False
            )
        )

        self.createq_tab.create_songs.clicked.connect(self._create_queue)

        self.tabs.setStyleSheet(TabStyle)

    def _create_queue(self):
        """
        Creates a queue of the songs in the QTableWidget under Queue Maker
        """
        # Get song IDs and create queue with them
        song_ids = []
        for row in range(self.createq_tab.queue_list.rowCount()):
            song_id = QTableWidgetItem(self.createq_tab.queue_list.item(row, 2).text())
            song_ids.append(song_id.text())

        self.user.create_queue(song_ids)
