import sys

from PyQt5.QtWidgets import (QMainWindow, QDialog, QWidget, QPushButton,
    QLineEdit, QHBoxLayout, QVBoxLayout, QApplication, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QVBoxLayout, QAction)

from client import Client
from user import User

SCOPE = 'user-modify-playback-state ' + \
        'playlist-read-private playlist-read-collaborative ' + \
        'playlist-modify-private playlist-modify-public '


class Login(QDialog):

    def __init__(self):
        """
        Login page. Pretty straightfoward.
        """
        super().__init__()
        self.button = QPushButton('Login', self)
        self.button.clicked.connect(self.login)
        self.input = QLineEdit()

        # Design the GUI
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.input)
        h_box.addWidget(self.button)
        h_box.addStretch()

        self.setLayout(h_box)
        self.setWindowTitle('Spearch')

    def login(self):
        """
        Login with text in the input. This creates a Client object which starts
        up the Spotify login. That's where the password is typed.
        """
        self.client = Client(self.input.text(), SCOPE)
        self.close()


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


class SongUI(QWidget):
    # TODO Add sort on click for song and artist column

    def __init__(self, parent, user):
        """
        Widget/tab that shows songs and artists for a given playlist
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

        # If a playlist is selected, run list_songs by passing the playlist ID
        # of the playlist chosen
        self.playlists.currentIndexChanged.connect(
            lambda: self.list_songs(
                self.user.pl_ids[self.playlists.currentIndex()]))

    def init_ui(self):
        # Create the stuff
        self.playlists = QComboBox(self)
        self.playlist_songs = QTableWidget(0, 2, self)
        self.playlist_songs.setHorizontalHeaderLabels(['Song', 'Artist'])
        self.playlists.addItems(self.user.playlists)

        # Style the list of songs
        header = self.playlist_songs.horizontalHeader()
        header.setStyleSheet('QHeaderView { font-weight: 600; font-size: 10pt;}')
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Put it all together
        v_box = QVBoxLayout()
        v_box.addWidget(self.playlists)
        v_box.addWidget(self.playlist_songs)
        self.setLayout(v_box)

    def list_songs(self, pl_id):
        """
        Adds the songs and their artists from a playlist to the Table Widget

        Parameters:
        pl_id - The ID of the playlist
        """
        # Get the song data
        songs = self.user.get_playlist_songs(pl_id)
        # Reset the table widget
        self.playlist_songs.clear()
        self.playlist_songs.setHorizontalHeaderLabels(['Song', 'Artist'])
        self.playlist_songs.verticalHeader().setVisible(False)
        # Remove every row to redo (less efficient but much simpler)
        for _ in range(self.playlist_songs.rowCount()):
            self.playlist_songs.removeRow(0)

        # Add the songs as adding each row
        for n, song in enumerate(songs):
            self.playlist_songs.insertRow(n)
            self.playlist_songs.setItem(n, 0, QTableWidgetItem(song[0]))
            self.playlist_songs.setItem(n, 1, QTableWidgetItem(', '.join(song[2])))


class QueueUI(QWidget):

    def __init__(self, parent, user):
        """
        Widget/tab that allows the creation of a queue given some logic
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

    def init_ui(self):
        pass


def main():
    app = QApplication(sys.argv)

    # Login
    login = Login()
    login.exec_()

    # Do actual stuff
    window = Window(login.client)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

#self.volume = QSlider(QtCore.Qt.Horizontal)
#self.volume.setMinimum(0)
#self.volume.setMaximum(100)
#self.volume.setValue(10)
#self.volume.setTickInterval(10)
#self.volume.setTickPosition(QSlider.TicksBelow)
#self.volume.valueChanged.connect(<function to change volume>)

# bar = self.menuBar()
# file = bar.addMenu('File')
# save = QtWidgets.QAction('Save', self)
# save.setShortcut('Ctrl+S')
# file.addAction(save)
# find = QtWidgets.QAction('Find All', self)
# find_menu = file.addMenu('Find')
# find_menu.addAction(find)
# save.triggered.connect(function for it)
