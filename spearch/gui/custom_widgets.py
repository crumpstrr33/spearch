from PyQt5.QtWidgets import (QTableWidget, QAbstractItemView, QHeaderView,
    QTableWidgetItem, QWidget, QVBoxLayout, QGroupBox, QPushButton, QCheckBox,
    QMenu, QAction)
from PyQt5.QtCore import Qt

from style import BG_COLOR


class SimpleFilterArtistsTable(QTableWidget):
    """
    When right-clicked, it gives an option to delete the cell clicked in.
    Otherwise, just a normal QTableWidget.
    """

    def mousePressEvent(self, event):
        if (event.button() == Qt.RightButton and
            self.rowAt(event.pos().y()) != -1):
            delete = QAction('Delete', self)
            delete.triggered.connect(lambda:
                self.removeRow(self.rowAt(event.pos().y())))

            self.menu = QMenu(self)
            self.menu.addAction(delete)
            self.menu.exec_(event.globalPos())


class SongDataTableWidget(QTableWidget):

    def __init__(self, selectable, sortable, parent=None):
        """
        A customized version of the QTableWidget. It is used for listing and
        displaying song data.

        Parameters:
        selectable - If True, the contents of the table can be selected,
                     otherwise they cannot.
        sortable - Able to be sorted by clicking on a column header if True and
                   not if False.
        parent - (default None) Parent this widget.
        """
        super().__init__(0, 3, parent)

        # Customization
        self.selectable = selectable
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
        # Make each column take up half of the total table width
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Remove the indexing on the side
        self.verticalHeader().setVisible(False)

    def add_songs(self, songs, reset, selected=None):
        """
        Will add the song data pass to the table.

        Parameters:
        songs - The song data to add. This data is in the form:
                [<name>, (<artist1>, <artist2>, ...), <id>]
                Or as a QTableWidget which it'll pull the info from.
        reset - Will reset the table first if True, otherwise appends new songs
                onto the end.
        selected - If True, will add only the songs that have been selected
                   (only if songs is a QTableWidget)
        """
        # Get current row number
        if reset:
            # Reset table by deleting ever row
            for _ in range(self.rowCount()):
                self.removeRow(0)
            row_count = 0
        else:
            row_count = self.rowCount()

        # Must disable sorting before adding the new songs
        if self.sortable:
            self.setSortingEnabled(False)

        # Whether it's a list of song data or a QTableWidget
        if not isinstance(songs, QTableWidget):
            # Iterate through each song
            for row, song_data in enumerate(songs):
                # Current row index
                ind = row + row_count

                # Create the new row
                self.insertRow(ind)

                # Create song, artist and ID widget items
                song = QTableWidgetItem(song_data[0])
                artist = QTableWidgetItem(', '.join(song_data[1]))
                song_id = QTableWidgetItem(song_data[2])

                self._add_row(ind, song, artist, song_id)
        else:
            # Get the songs from the song list
            if selected:
                row_nums = [x.row() for x in songs.selectedIndexes()]
            else:
                row_nums = range(songs.rowCount())

            num_skipped = 0
            for n, row in enumerate(row_nums):
                # Skip song if no ID
                if not songs.item(row, 2).text():
                    num_skipped += 1
                    continue

                # Current row index
                ind = row_count + n - num_skipped

                # Create row
                self.insertRow(ind)

                # Create song, artist and ID widget items
                song = QTableWidgetItem(songs.item(row, 0))
                artist = QTableWidgetItem(songs.item(row, 1).text())
                song_id =  QTableWidgetItem(songs.item(row, 2).text())

                self._add_row(ind, song, artist, song_id)

        # Enable sorting if wanted
        if self.sortable:
            self.setSortingEnabled(True)

    def _add_row(self, row_ind, song, artist, song_id):
        """
        Adds a row to the table
        """
        # Disable selecting if not wanted
        if not self.selectable:
            song.setFlags(Qt.ItemIsEnabled)
            song.setFlags(Qt.ItemIsSelectable)
            artist.setFlags(Qt.ItemIsEnabled)
            artist.setFlags(Qt.ItemIsSelectable)

        # Inset info
        self.setItem(row_ind, 0, song)
        self.setItem(row_ind, 1, artist)
        self.setItem(row_ind, 2, song_id)


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
        layout - The layout that the QGroupbox will be for.
        parent - (default None) The parent of this widget.
        """
        super().__init__(parent=parent)
        self.widget_type = widget_type

        # Create outter layout (to contain the QGroupBox)
        self.layout = QVBoxLayout(self)
        # Pad the top to give room for the widget
        self.layout.setContentsMargins(0, 20, 0, 0)
        # Create the QGroupBox and set it's layout
        self.groupbox = QGroupBox(title, self)
        self.groupbox.setLayout(layout)
        # Create the desired widget and add to layout
        self.title_widget = self._get_widget(widget_type, widget_name)
        self.layout.addWidget(self.groupbox)

        # Shift the widget down to align with the title
        self.title_widget.move(widget_placement, 15)

    def _get_widget(self, widget_type, widget_name):
        """
        Gets the appropriate widget. Supports the following widgets:
        QPushButton, QCheckBox.
        """
        if widget_type == 'QPushButton':
            widget = QPushButton(widget_name, parent=self)
            # Make the button smaller with all this
            widget.setStyleSheet('''
                font-size: 10px;
            ''')
            widget.setMaximumHeight(22)
            width = widget.fontMetrics().boundingRect(widget_name).width()
            widget.setFixedWidth(1.2 * width)
        elif widget_type == 'QCheckBox':
            widget = QCheckBox(widget_name, parent=self)
            # Centers the checkbox in the whitespace
            widget.setStyleSheet('''
                margin-bottom: 10px;
                background: {};
                padding-left: 6px;
            '''.format(BG_COLOR))
            widget.setMaximumWidth(46)

        return widget
