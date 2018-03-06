from PyQt5.QtWidgets import (QWidget, QComboBox, QTableWidget, QHeaderView,
    QVBoxLayout, QHBoxLayout, QTableWidgetItem, QPushButton, QAbstractItemView,
    QListWidget)
from PyQt5 import QtCore


class SongUI(QWidget):

    def __init__(self, parent, user):
        """
        Widget/tab that shows songs and artists for a given playlist
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

        # Display the songs of a playlist that is selected from the combo box
        self.playlists.currentIndexChanged.connect(
            lambda: self.list_songs(
                self.user.pl_ids[self.playlists.currentIndex()]))

    def init_ui(self):
        # Create list for selection of playlists
        self.playlists = QComboBox(self)
        # Add playlists to the combo box
        self.playlists.addItems(self.user.playlists)

        # Create button to add songs to queue
        self.add_songs = QPushButton('Add', self)
        self.add_songs.setMaximumWidth(1.2 * self.add_songs.width())

        # Create song list
        self.songs_table = QTableWidget(0, 3, self)
        self.songs_table.setHorizontalHeaderLabels(['Songs', 'Artists'])
        self.songs_table.setShowGrid(False)
        self.songs_table.verticalHeader().setVisible(False)
        # Doesn't allow editing
        self.songs_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Hidden column containing song IDs
        self.songs_table.setColumnHidden(2, True)
        # Styling of Songs and Artists headers
        header = self.songs_table.horizontalHeader()
        header.setStyleSheet('QHeaderView { font-weight: 600; font-size: 10pt;}')
        # Stretch to fill space and apply styling to header
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        # Put it all together
        h_box1 = QHBoxLayout()
        h_box1.addWidget(self.add_songs)
        h_box1.addWidget(self.playlists)
        v_box = QVBoxLayout()
        v_box.addLayout(h_box1)
        v_box.addWidget(self.songs_table)
        self.setLayout(v_box)

    def list_songs(self, pl_id):
        """
        Adds the songs and their artists from a playlist to the Table Widget

        Parameters:
        pl_id - The ID of the playlist
        """
        # Get the song data
        songs = self.user.get_playlist_songs(pl_id)

        # Reset the data by removing old songs and whatnot
        for _ in range(self.songs_table.rowCount()):
            self.songs_table.removeRow(0)
        self.songs_table.setSortingEnabled(False)

        for n, song in enumerate(songs):
            # Create the row
            self.songs_table.insertRow(n)

            # Add song name
            self.songs_table.setItem(n, 0, QTableWidgetItem(song[0]))

            # Add artist(s)
            artist = QTableWidgetItem(', '.join(song[1]))
            # Remove the ability to select it
            artist.setFlags(QtCore.Qt.ItemIsEnabled)
            artist.setFlags(QtCore.Qt.ItemIsSelectable)
            self.songs_table.setItem(n, 1, artist)

            # Hidden column with song IDs
            self.songs_table.setItem(n, 2, QTableWidgetItem(song[2]))

        self.songs_table.setSortingEnabled(True)


class CreateQueueUI(QWidget):

    def __init__(self, parent, user):
        """
        Widget/tab that allows the creation of a queue given some logic
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

        # Clear the queue list
        self.clear_songs.clicked.connect(self.clear_queue)

    def init_ui(self):
        # Button to add songs to queue
        self.create_songs = QPushButton('Create', self)
        # Button to clear songs from queue
        self.clear_songs = QPushButton('Clear', self)

        # List of songs and their artists
        self.queue_list = QTableWidget(0, 3, self)
        self.queue_list.setHorizontalHeaderLabels(['Song', 'Artist'])
        self.queue_list.setShowGrid(False)
        self.queue_list.verticalHeader().setVisible(False)
        # Doesn't allow editing
        self.queue_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Hidden column containing song IDs
        self.queue_list.setColumnHidden(2, True)
        # Style the list of songs
        header = self.queue_list.horizontalHeader()
        header.setStyleSheet('QHeaderView { font-weight: 600; font-size: 10pt;}')
        # Each column takes up 50% of the available horizontal space
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        v_box = QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.create_songs)

        h_box = QHBoxLayout()
        h_box.addLayout(v_box)
        h_box.addWidget(self.queue_list)
        self.setLayout(h_box)

    def clear_queue(self):
        """
        Removes all of the songs from the queue list maker
        """
        # Reset the data by removing old songs and whatnot
        for _ in range(self.queue_list.rowCount()):
            self.queue_list.removeRow(0)


class CurrentQueueUI(QWidget):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.init_ui()

    def init_ui(self):
        # List of songs and their artists
        self.current_queue = QTableWidget(0, 3, self)
        self.current_queue.setHorizontalHeaderLabels(['Song', 'Artist'])
        self.current_queue.setShowGrid(False)
        # Doesn't allow editing
        self.current_queue.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Hidden column containing song IDs
        self.current_queue.setColumnHidden(2, True)
        # Style the list of songs
        header = self.current_queue.horizontalHeader()
        header.setStyleSheet('QHeaderView { font-weight: 600; font-size: 10pt;}')
        # Each column takes up 50% of the available horizontal space
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        v_box = QVBoxLayout()
        v_box.addWidget(self.current_queue)

        self.setLayout(v_box)
