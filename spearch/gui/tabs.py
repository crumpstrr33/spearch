from collections import defaultdict
from json import dumps

from PyQt5.QtWidgets import (QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QPushButton, QGridLayout, QLineEdit, QWidgetItem,
    QCheckBox, QLabel)
from PyQt5 import QtCore

from custom_widgets import SongArtistTableWidget
from popups import NewPlaylistDialog


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
            lambda: self.add_songs(
                self.user.pl_ids[self.playlists.currentIndex()]))

    def init_ui(self):
        # Create list for selection of playlists
        self.playlists = QComboBox(self)
        # Add playlists to the combo box
        self.playlists.addItems(self.user.playlists)

        # Create button to add songs to queue
        self.add_songs_button = QPushButton('Add', self)
        self.add_songs_button.setMaximumWidth(1.2 * self.add_songs_button.width())

        # Create song list
        self.songs_table = SongArtistTableWidget(self, select_artists=False)

        # Put it all together
        top_row = QHBoxLayout()
        top_row.addWidget(self.add_songs_button)
        top_row.addWidget(self.playlists)
        v_box = QVBoxLayout(self)
        v_box.addLayout(top_row)
        v_box.addWidget(self.songs_table)

    def add_songs(self, pl_id):
        """
        Gets the songs, from the currently selected playlist and adds them to
        the table

        Parameters:
        pl_id - The ID of the playlist
        """
        songs = self.user.get_playlist_songs(pl_id)
        self.songs_table.add_songs(songs)


class FilterUI(QWidget):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.init_ui()

        self.commit.clicked.connect(self.get_layout_data)

    def init_ui(self):
        # Button to add a playlist filter
        self.add_pl = QPushButton('Add Playlist', self)
        self.add_pl.clicked.connect(self.add_playlist)
        # Button to show what songs are return by total filter
        self.commit = QPushButton('Commit', self)
        # Create button to add songs to queue
        self.add_songs_button = QPushButton('Add', self)
        self.add_songs_button.setMaximumWidth(1.2 * self.add_songs_button.width())
        # Table to show filtered songs
        self.songs_table = SongArtistTableWidget(self, False, False, False)

        # Total layout for playlist filters
        self.filt_layout = QGridLayout()
        self.filt_layout.addWidget(self.add_pl, 1000, 0)

        # Put it all together
        h_box_buttons = QHBoxLayout()
        h_box_buttons.addWidget(self.add_songs_button)
        h_box_buttons.addWidget(self.commit)
        v_box = QVBoxLayout()
        v_box.addLayout(h_box_buttons)
        v_box.addWidget(self.songs_table)
        h_box = QHBoxLayout(self)
        h_box.addLayout(self.filt_layout)
        h_box.addLayout(v_box)

    def get_layout_data(self):
        """
        From the data inputted on this tab, get the data in a proper format
        to pass along to self.user.filter_playlist. If there are overlaps
        (i.e. two ANDs for a single playlist or artist_or's), then they are
        combined/concatenated
        """
        # Get the data in a dict
        filt_dict, _ = self.parse_filt_layout()
        # Clean the data up to pass to self.user.filter_playlist
        filt_dict = self.sanitize_data(filt_dict)

        filt_songs = []
        # For each playlist, get the filtered song list
        for pl, pl_data in filt_dict.items():
            songs = self.user.get_playlist_songs(
                self.user.pl_ids[self.user.playlists.index(pl)])
            filt_songs += self.user.filter_playlist(songs, _or=pl_data)

        self.songs_table.add_songs(filt_songs)

    def parse_filt_layout(self, layout=None, depth=0, filt_dict=None, d_ind=0,
                          latest_pl=None, latest_logic=None, latest_filt=None):
        """
        Recursively queries the data from this tab to filt the playlist(s)
        selected. The arguments are used for the recursive-ness.

        This works since each important part of the layout is a separate and
        nested layout. So there's the parent one. Then a playlist layout, a
        nested logic layout and a nested (in the logic layout) filter layout.
        Playlist just means the name of the playlist. Logic is whether it's
        an AND or an OR. And filter is the filter choice of which there are
        seven described under User.filter_playlist. These are stored in a
        recursive dictionary where each key has a unique ID attached to the
        end (d_ind) so that duplicates can be used.

        Parameters:
        layout - (default None) The layout to parse as described above
        depth - (default 0) The number of times the method has been recursively
                called which allows us to know what Combobox has been reached
        filt_dict - (default None) The main dictionary that stores all of the
                    parsed data
        d_ind - (default 0) The number of total entries to filt_dict, this
                includes child dicts which maintains unique key names
        latest_pl - (default None) The last playlist name used so that it can
                    be called in the dictionary for adding data
        latest_logic - (default None) The last type of logic used like latest_pl
        latest_filt - (default None) The last filter type used like latest_pl
        """
        # The layout that is being parsed
        layout = layout or self.filt_layout
        # The dictionary that all the data is being added to
        filt_dict = filt_dict or {}

        # Run through each item of the layout
        for ind in range(layout.count()):
            item = layout.itemAt(ind)
            # If it's a widget...
            if isinstance(item, QWidgetItem):
                # and a Combobox...
                if isinstance(item.widget(), QComboBox):
                    item_key = item.widget().currentText() + '&&' + str(d_ind)
                    d_ind += 1
                    # A recursive depth of 1 is the playlist name
                    if depth == 1:
                        filt_dict[item_key] = {}
                        latest_pl = item_key
                    # A recursive depth of 2 is the logic name
                    if depth == 2:
                        filt_dict[latest_pl][item_key] = {}
                        latest_logic = item_key
                    # A recursive depth of 3 is the filter type
                    if depth == 3:
                        filt_dict[latest_pl][latest_logic][item_key] = ''
                        latest_filt = item_key
                # and a LineEdit
                elif isinstance(item.widget(), QLineEdit):
                    # Add comma separated keywords for the filter
                    filt_kw = list(map(lambda x: x.strip(),
                        item.widget().displayText().split(',')))
                    filt_dict[latest_pl][latest_logic][latest_filt] = filt_kw
                # and Checkbox for whether NOT is chosen or not
                elif isinstance(item.widget(), QCheckBox):
                    filt_dict[latest_pl][latest_logic]['NOT'] = item.widget().isChecked()
            # or if it's a GridLayout
            elif isinstance(item, QGridLayout):
                # Recursively run the method with the child layout and current
                # data
                filt_dict, d_ind = self.parse_filt_layout(layout=item,
                        depth=depth + 1, filt_dict=filt_dict, d_ind=d_ind,
                        latest_pl=latest_pl, latest_logic=latest_logic,
                        latest_filt=latest_filt)

        # Return current data that has been parsed
        return filt_dict, d_ind

    @staticmethod
    def sanitize_data(filt_dict):
        """
        Cleans up the dictionary returned by self.parse_filt_layout
        """
        clean_dict = defaultdict(list)
        # Each key of dictionary is a playlist name
        for pl, pl_data in filt_dict.items():
            clean_pl = pl.split('&&')[0]
            # Each playlist has a main AND or OR logic
            clean_dict[clean_pl] = {'_and': [], '_or': []}
            # Look at each logic chosen
            for logic, logic_data in pl_data.items():
                clean_logic = '_and' if logic.startswith('AND') else '_or'
                # Init the logic dict for the filter
                clean_dict[clean_pl][clean_logic].append({})
                for filt, filt_data in logic_data.items():
                    # Add NOT to dict
                    if filt == 'NOT':
                        clean_dict[clean_pl][clean_logic][-1]['_not'] = filt_data
                        continue

                    clean_filt = filt.split('&&')[0]
                    # For each AND, append dict to the AND list and same for OR
                    clean_dict[clean_pl][clean_logic][-1][clean_filt] = filt_data

        return clean_dict

    def add_playlist(self):
        """
        Create another selection from playlists for filtering
        """
        # Create list for selection of playlists
        new_pl = QComboBox(self)
        new_pl.addItems(self.user.playlists)
        # Add AND/OR logic selection
        new_logic_add = QPushButton('Add Logic', self)
        # Remove current playlist
        new_pl_remove = QPushButton('Remove Playlist', self)

        # Grid made for each playlist choice
        new_pl_grid = QGridLayout()
        new_pl_grid.addWidget(new_pl, 0, 0)
        new_pl_grid.addWidget(new_pl_remove, 0, 1)
        new_pl_grid.addWidget(new_logic_add, 1000, 0)

        # Button click to add a new logic ComboBox
        new_logic_add.clicked.connect(lambda: self.add_logic(new_pl_grid))
        # Button click to remove current playlist
        new_pl_remove.clicked.connect(lambda: self.remove_layout(new_pl_grid))

        # Add to total layout
        self.filt_layout.addLayout(new_pl_grid, self.filt_layout.count(), 0)

    def add_logic(self, pl_layout):
        """
        Add another selection of logic for filtering for some playlist
        """
        # Add AND/OR logic selection
        new_logic = QComboBox(self)
        new_logic.addItems(['AND', 'OR'])

        # Button to add a filter combobox
        new_filter_add = QPushButton('Add Filter', self)

        # Remove AND/OR logic selection
        new_logic_remove = QPushButton('Remove Logic', self)

        # NOT choice for AND/OR logic
        new_not_check = QCheckBox(self)
        # NOT text
        new_not_text = QLabel('Not', self)

        # Create grid for each block of AND/OR logic
        new_logic_grid = QGridLayout()
        new_logic_grid.addWidget(new_logic, new_logic_grid.count(), 0)
        new_logic_grid.addWidget(new_not_check, new_logic_grid.count() - 1, 1)
        new_logic_grid.addWidget(new_not_text, new_logic_grid.count() - 2, 2)
        new_logic_grid.addWidget(new_logic_remove, new_logic_grid.count() - 3, 3)
        new_logic_grid.addWidget(new_filter_add, 1000, 0)

        # Add a new filter combobox if this button is clicked
        new_filter_add.clicked.connect(lambda:
            self.add_filter(new_logic_grid))

        # Remove the clicked logic and all of the filter options
        new_logic_remove.clicked.connect(lambda:
            self.remove_layout(new_logic_grid))

        # Add new layout to the parent playlist layout
        pl_layout.addLayout(new_logic_grid, pl_layout.count(), 0, 1, 2)

    def add_filter(self, logic_layout):
        """
        Add another selection of filtering parameters for some logic
        """
        # Filter selection
        new_filter = QComboBox(self)
        new_filter.addItems(['artists_and', 'artists_or', 'artist_and',
                             'artist_or', 'song_exact', 'song_and', 'song_or'])

        # Input for the filtering
        new_filter_input = QLineEdit(self)

        # Button to remove filter selection
        new_filter_remove = QPushButton('Remove Filter', self)

        new_filter_grid = QGridLayout()
        new_filter_grid.addWidget(new_filter, new_filter_grid.count(), 0)
        new_filter_grid.addWidget(new_filter_remove, new_filter_grid.count() - 1, 1)
        new_filter_grid.addWidget(new_filter_input, new_filter_grid.count() - 1, 0)

        new_filter_remove.clicked.connect(lambda:
            self.remove_widgets(new_filter, new_filter_remove, new_filter_input))

        logic_layout.addLayout(new_filter_grid, logic_layout.count(), 0)

    def remove_layout(self, layout):
        """
        Removes everything from a layout and deletes the widgets recursively.
        So it will delete layouts in layouts, etc.
        """
        # Loop until layout is empty
        while layout.count():
            # If the current item in layout is a layout, repeat recursively,
            # else delete it
            item = layout.takeAt(0)
            if isinstance(item, (QGridLayout, QHBoxLayout, QVBoxLayout)):
                self.remove_layout(item)
            else:
                item.widget().deleteLater()
        # At the end, delete the layout
        self.filt_layout.removeItem(layout)

    def remove_widgets(self, *widgets):
        """
        Remove the logic ComboBox and the remove button
        """
        for widget in widgets:
            widget.deleteLater()

    # def list_songs(self, songs):
    #     """
    #     Adds the songs and their artists from a playlist to the Table Widget

    #     Parameters:
    #     songs - The songs to display
    #     """
    #     # Reset the data by removing old songs and whatnot
    #     for _ in range(self.songs_table.rowCount()):
    #         self.songs_table.removeRow(0)
    #     self.songs_table.setSortingEnabled(False)

    #     for n, song in enumerate(songs):
    #         # Create the row
    #         self.songs_table.insertRow(n)

    #         # Add song name
    #         self.songs_table.setItem(n, 0, QTableWidgetItem(song[0]))

    #         # Add artist(s)
    #         artist = QTableWidgetItem(', '.join(song[1]))
    #         # Remove the ability to select it
    #         artist.setFlags(QtCore.Qt.ItemIsEnabled)
    #         artist.setFlags(QtCore.Qt.ItemIsSelectable)
    #         self.songs_table.setItem(n, 1, artist)

    #         # Hidden column with song IDs
    #         self.songs_table.setItem(n, 2, QTableWidgetItem(song[2]))

    #     self.songs_table.setSortingEnabled(True)


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

        # Make playlist
        self.create_playlist.clicked.connect(self.make_new_playlist)

    def init_ui(self):
        # Button to add songs to queue
        self.create_songs = QPushButton('Create', self)
        # Button to clear songs from queue
        self.clear_songs = QPushButton('Clear', self)
        # Button to save current songs to a new playlist
        self.create_playlist = QPushButton('Make Playlist', self)

        # List of songs and their artists
        self.queue_list = SongArtistTableWidget(self)

        # Put it all together
        v_box = QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.create_playlist)
        v_box.addWidget(self.clear_songs)
        v_box.addWidget(self.create_songs)

        h_box = QHBoxLayout(self)
        h_box.addLayout(v_box)
        h_box.addWidget(self.queue_list)

    def clear_queue(self):
        """
        Removes all of the songs from the queue list maker
        """
        # Reset the data by removing old songs and whatnot
        for _ in range(self.queue_list.rowCount()):
            self.queue_list.removeRow(0)

    def make_new_playlist(self):
        """
        Creates a new playlist from the current listed songs
        """
        playlist_name, private, ok = NewPlaylistDialog.getPlaylistName()

        if ok:
            song_ids = [self.queue_list.item(row, 2).text() for row in
                            range(self.queue_list.rowCount())]
            self.user.create_playlist(song_ids, playlist_name, not private)


class CurrentQueueUI(QWidget):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.init_ui()

    def init_ui(self):
        # List of songs and their artists
        self.current_queue = SongArtistTableWidget(self)

        v_box = QVBoxLayout(self)
        v_box.addWidget(self.current_queue)
