from PyQt5.QtWidgets import (QTableWidget, QAbstractItemView, QHeaderView,
    QTableWidgetItem, QWidget, QVBoxLayout, QGroupBox, QPushButton, QCheckBox)
from PyQt5 import QtCore

from style import *


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


class WidgetGroupBox(QWidget):

    def __init__(self, title, widget_type, widget_name, widget_placement,
                 layout, parent=None):
        """
        A slightly customized QGroupBox widget where a widget is found aside
        the title of the groupbox.

        Parameters:
        title - Title of the QGroupBox
        widget_type - The type of widget to appear next to the title, current
                      options are 'QPushButton' and 'QCheckBox'
        widget_name - The name to appear for the widget
        widget_placement - Where on the top border of the QGroupBox should the
                           widget appear, the higher the number, the further to
                           the right it is
        layout - The layout that the QGroupbox will be for
        parent - (default None) The parent of the WidgetGroupBox
        """
        super().__init__(parent=parent)

        # Create outter layout (to contain the QGroupBox)
        self.layout = QVBoxLayout(self)
        # Pad the top to give room for the widget
        self.layout.setContentsMargins(0, 24, 0, 0)
        # Create the QGroupBox and set it's layout and style
        self.groupbox = QGroupBox(title, self)
        self.groupbox.setLayout(layout)
        self.groupbox.setStyleSheet(GroupBoxStyle)
        # Create the desired widget and add to layout
        self.title_widget = self._get_widget(widget_type, widget_name)
        self.layout.addWidget(self.groupbox)

        # Shift the widget down to align with the title
        self.title_widget.move(widget_placement, 24)

    def _get_widget(self, widget_type, widget_name):
        """
        Gets the appropriate widget. Supports the following widgets:
        QPushButton, QCheckBox.
        """
        if widget_type == 'QPushButton':
            widget = QPushButton(widget_name, parent=self)
        elif widget_type == 'QCheckBox':
            widget = QCheckBox(widget_name, parent=self)
            # Centers the checkbox in the whitespace
            widget.setStyleSheet('background: white; padding-left: 25px;')
            widget.stateChanged.connect(self._toggle_border_color)

        return widget

    def _toggle_border_color(self):
        """
        Toggles the border style if the checkmark is chosen and toggled.
        """
        if self.groupbox.styleSheet() == GroupBoxStyle:
            self.groupbox.setStyleSheet(GroupBoxToggleStyle)
        else:
            self.groupbox.setStyleSheet(GroupBoxStyle)
