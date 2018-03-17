from PyQt5.QtWidgets import (QTableWidget, QAbstractItemView, QHeaderView)

SongArtistHeaderStyle = '''
QHeaderView {
    font-weight: 600;
    font-size: 10pt;
}
'''


class SongArtistTableWidget(QTableWidget):

    def __init__(self, parent):
        super().__init__(0, 3, parent)

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
