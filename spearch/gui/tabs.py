from collections import defaultdict

from PyQt5.QtWidgets import (QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
    QPushButton, QGridLayout, QLineEdit, QWidgetItem, QCheckBox, QLabel,
    QGroupBox)
from PyQt5 import QtCore

from custom_widgets import SongArtistTableWidget, ButtonGroupBox, CheckboxGroupBox
from popups import NewPlaylistDialog


class PlaylistSongsUI(QWidget):

    def __init__(self, parent, user):
        """
        Tab that shows songs and artists for a given playlist. Songs
        from the list can be chosen and added to the Queue Maker tab via
        the Add button.
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

        # Display the songs of a playlist that is selected from the combo box
        self.playlists.currentIndexChanged.connect(
            lambda: self.add_songs(
                self.user.pl_ids[self.playlists.currentIndex()]))

    def init_ui(self):
        # Create song list
        self.songs_table = SongArtistTableWidget(self, select_artists=False)

        # Create list for selection of playlists
        self.playlists = QComboBox(self)
        # Add playlists to the combo box
        self.playlists.addItems(self.user.playlists)
        # Init add all the songs of the first playlist
        self.add_songs(self.user.pl_ids[0])

        # Create button to add songs to queue
        self.add_songs_button = QPushButton('Add', self)
        self.add_songs_button.setMaximumWidth(1.2 * self.add_songs_button.width())

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


class FilterPlaylistsUI(QWidget):
    ADD_PLAYLIST_WIDTH = 500

    def __init__(self, parent, user, max_height, max_width):
        """
        Tab where songs can be chosen via filtering of playlist(s) and logic
        which can be shown via the Commit button. The filtered songs can be
        added to the Queue Maker tab via the Add button.
        """
        super().__init__(parent)
        self.max_height = max_height
        self.max_width = max_width

        self.user = user
        self.init_ui()

        self.commit.clicked.connect(self.get_layout_data)

    def init_ui(self):
        # Button to add a playlist filter
        self.add_pl = QPushButton('Add Playlist', self)
        self.add_pl.clicked.connect(self.add_playlist)
        self.add_pl.setFixedWidth(self.ADD_PLAYLIST_WIDTH)
        # Button to show what songs are return by total filter
        self.commit = QPushButton('Commit', self)
        self.commit.setMaximumWidth(self.max_width / 4)
        # Create button to add songs to queue
        self.add_songs_button = QPushButton('Add', self)
        self.add_songs_button.setMaximumWidth(self.max_width / 4)
        # Table to show filtered songs
        self.songs_table = SongArtistTableWidget(self, False, False, False)
        self.songs_table.setMaximumWidth(self.max_width - self.ADD_PLAYLIST_WIDTH)

        # Total layout for playlist filters
        self.filt_layout = QGridLayout()
        self.filt_layout.addWidget(self.add_pl, 1000, 0)
        self.filt_layout.setRowStretch(999, 1)

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
        filt_dict, _ = self._parse_filt_layout()
        # Clean the data up to pass to self.user.filter_playlist
        filt_dict = self.sanitize_data(filt_dict)

        filt_songs = []
        # For each playlist, get the filtered song list
        for pl, pl_data in filt_dict.items():
            songs = self.user.get_playlist_songs(
                self.user.pl_ids[self.user.playlists.index(pl)])
            filt_songs += self.user.filter_playlist(songs, _or=pl_data)

        self.songs_table.add_songs(filt_songs)

    def _parse_filt_layout(self, layout=None, depth=0, filt_dict=None, d_ind=0,
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
                filt_dict, d_ind = self._parse_filt_layout(layout=item,
                        depth=depth + 1, filt_dict=filt_dict, d_ind=d_ind,
                        latest_pl=latest_pl, latest_logic=latest_logic,
                        latest_filt=latest_filt)

        # Return current data that has been parsed
        return filt_dict, d_ind

    @staticmethod
    def sanitize_data(filt_dict):
        """
        Cleans up the dictionary returned by self._parse_filt_layout
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
        pl_choice = QComboBox()
        pl_choice.addItems(self.user.playlists)
        pl_choice.setContentsMargins(150, 150, 150, 150)
        # Add AND/OR logic selection
        add_logic = QPushButton('Add Logic')

        # Grid made for each playlist choice
        pl_grid = QGridLayout()
        pl_grid.addWidget(pl_choice, 0, 0)
        pl_grid.addWidget(add_logic, 1000, 0)
        # Push everything to the top of the layout
        pl_grid.setRowStretch(1001, 1)

        # Create border with the remove button for the playlist
        pl_group_box = ButtonGroupBox('Playlist', 'Remove', 370, pl_grid)

        # Button click to add a new logic ComboBox
        add_logic.clicked.connect(lambda: self.add_logic(pl_grid))
        # Button click to remove current playlist
        pl_group_box.title_button.clicked.connect(lambda: pl_group_box.deleteLater())

        # Add to total layout
        self.filt_layout.addWidget(pl_group_box, self.filt_layout.count(), 0)

    def add_logic(self, pl_layout):
        """
        Add another selection of logic for filtering for some playlist. It
        consists of a Groupbox titled 'Logic' containing a Groubox for AND
        logic and another for OR logic.
        """
        # Create grid layout for the logic section
        logic_grid = QGridLayout()

        # Create Groupbox for the logic section
        logic_group_box = ButtonGroupBox('Logic', 'Remove', 320, logic_grid)

        # Remove button for logic Groupbox removes it
        logic_group_box.title_button.clicked.connect(lambda: logic_group_box.deleteLater())

        # Create grid layout for the AND logic section
        and_grid = QGridLayout()
        # Create groupbox for AND section
        and_group_box = CheckboxGroupBox('AND', 'Not', 200, and_grid)
        # Add the groupbox to the grid layout for the entire logic section
        logic_grid.addWidget(and_group_box, logic_grid.count(), 0)
        # Create button to add filters, add the functionality and add to layout
        and_add_filter = QPushButton('Add Filter')
        and_add_filter.clicked.connect(lambda: self.add_filter(and_grid))
        and_grid.addWidget(and_add_filter, 1000, 0)

        # Create grid layout for the OR logic section
        or_grid = QGridLayout()
        # Create groupbox for OR section
        or_group_box = CheckboxGroupBox('OR', 'Not', 200, or_grid)
        # Add the groupbox to the grid layout for the entire logic section
        logic_grid.addWidget(or_group_box, logic_grid.count(), 0)
        # Create button to add filters, add the functionality and add to layout
        or_add_filter = QPushButton('Add Filter')
        or_add_filter.clicked.connect(lambda: self.add_filter(or_grid))
        or_grid.addWidget(or_add_filter, 1000, 0)

        # Add the entire groupbox to the parent layout
        pl_layout.addWidget(logic_group_box, pl_layout.count(), 0)

    def add_filter(self, logic_layout):
        """
        Add another selection of filtering parameters for some logic
        """
        # Filter selection
        filter_choice = QComboBox()
        filter_choice.addItems(['artists_and', 'artists_or', 'artist_and',
                             'artist_or', 'song_exact', 'song_and', 'song_or'])

        # Input for the filtering
        filter_input = QLineEdit()

        # Button to remove filter selection
        filter_remove = QPushButton('Remove')

        filter_grid = QGridLayout()
        filter_grid.addWidget(filter_choice, filter_grid.count(), 0)
        filter_grid.addWidget(filter_remove, filter_grid.count() - 1, 1)
        filter_grid.addWidget(filter_input, filter_grid.count() - 1, 0)

        filter_remove.clicked.connect(lambda:
            self.remove_widgets(filter_choice, filter_remove, filter_input))

        logic_layout.addLayout(filter_grid, logic_layout.count(), 0)

    def remove_widgets(self, *widgets):
        """
        Remove the logic ComboBox and the remove button
        """
        for widget in widgets:
            widget.deleteLater()


class QueueMakerUI(QWidget):

    def __init__(self, parent, user):
        """
        Tab where songs are added from the Playlist Songs and Filter Playlists
        tabs. A new playlist can be made via the Make Playlist button, the
        list can be cleared via the Clear button and the queue can be create
        via the Create button. When the queue is created, the list is added
        to the Current Queue tab and the queue starts to play.
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
        """
        Tab that shows the current queue which is created via the Create 
        button on the Queue Maker tab.
        """
        super().__init__(parent)
        self.user = user
        self.init_ui()

    def init_ui(self):
        # List of songs and their artists
        self.current_queue = SongArtistTableWidget(self)

        v_box = QVBoxLayout(self)
        v_box.addWidget(self.current_queue)
