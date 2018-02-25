from PyQt5.QtWidgets import (QWidget, QComboBox, QTableWidget, QHeaderView,
    QVBoxLayout, QTableWidgetItem)

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
        # Create the stuff
        self.playlists = QComboBox(self)
        self.playlist_songs = QTableWidget(0, 2, self)

        # Add column headers to song list
        self.playlist_songs.setHorizontalHeaderLabels(['Song', 'Artist'])
        # Add playlists to the combo box
        self.playlists.addItems(self.user.playlists)

        # Style the list of songs
        header = self.playlist_songs.horizontalHeader()
        header.setStyleSheet('QHeaderView { font-weight: 600; font-size: 10pt;}')
        # Each column takes up 50% of the available horizontal space
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

        # Reset the table widget, must disable sorting first otherwise the
        # repopulating of the artist column is messed up
        self.playlist_songs.setSortingEnabled(False)
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

        # Turn sorting back on after populating the fields
        self.playlist_songs.setSortingEnabled(True)


class QueueUI(QWidget):
    # TODO All of it

    def __init__(self, parent, user):
        """
        Widget/tab that allows the creation of a queue given some logic
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

    def init_ui(self):
        pass
