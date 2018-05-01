from PyQt5.QtWidgets import (QTableWidget, QAbstractItemView, QHeaderView,
    QTableWidgetItem, QWidget, QVBoxLayout, QGroupBox, QPushButton)
from PyQt5 import QtCore

SongArtistHeaderStyle = '''
QHeaderView {
    font-weight: 600;
    font-size: 10pt;
}
'''
ButtonGroupBoxPadding = '''
QGroupBox {
    border: 2px solid grey;
    border-radius: 5px;
    margin-top: 0.5em;
    padding: 25 25 25 0;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
}
'''


class SongArtistTableWidget(QTableWidget):

    def __init__(self, parent, select_songs=True, select_artists=True,
                 sortable=True):
        super().__init__(0, 3, parent)

        # Customization
        self.select_songs = select_songs
        self.select_artists = select_artists
        self.sortable = sortable

        # Give the headers for Song and Artists
        self.setHorizontalHeaderLabels(['Song', 'Artists'])
        # Remove the gridlines of the table
        self.setShowGrid(False)
        # Remove editing of the cells
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Hide the ID column so that data can be used but is invisible
        self.setColumnHidden(2, True)

        # Style the table
        header = self.horizontalHeader()
        header.setStyleSheet(SongArtistHeaderStyle)
        # Make each column take up half of the total table width
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def add_songs(self, songs):
        """
        Will add the song data pass to the table.

        Parameters:
        songs - The song data to add. This data is in the form:
                [<name>, (<artist1>, <artist2>, ...), <id>]
        """
        # Reset table by deleting ever row
        for _ in range(self.rowCount()):
            self.removeRow(0)
        # Must disable sorting before adding the new songs
        if self.sortable:
            self.setSortingEnabled(False)

        # Iterate through each song
        for row, song_data in enumerate(songs):
            # Create the new row
            self.insertRow(row)

            # Create song widget item
            song = QTableWidgetItem(song_data[0])
            # Disable selecting if wanted
            if not self.select_songs:
                song.setFlags(QtCore.Qt.ItemIsEnabled)
                song.setFlags(QtCore.Qt.ItemIsSelectable)
            # Insert song name
            self.setItem(row, 0, song)

            # Create artist widget item
            artist = QTableWidgetItem(', '.join(song_data[1]))
            # Disable selecting if wanted
            if not self.select_artists:
                artist.setFlags(QtCore.Qt.ItemIsEnabled)
                artist.setFlags(QtCore.Qt.ItemIsSelectable)
            # Insert artist name(s)
            self.setItem(row, 1, artist)

            # Add song ID to hidden row
            self.setItem(row, 2, QTableWidgetItem(song_data[2]))

        # Enable sorting if wanted
        if self.sortable:
            self.setSortingEnabled(True)


class ButtonGroupBox(QWidget):

    def __init__(self, title, button_name, button_placement, grid, parent=None):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 24, 0, 0)
        self.groupBox = QGroupBox(title, self)
        self.groupBox.setLayout(grid)
        self.groupBox.setStyleSheet(ButtonGroupBoxPadding)
        self.title_button = QPushButton(button_name, parent=self)
        self.layout.addWidget(self.groupBox)

        self.title_button.move(button_placement, 24)
