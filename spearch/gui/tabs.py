from PyQt5.QtWidgets import (QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
    QPushButton, QGridLayout, QLineEdit, QWidgetItem, QCheckBox, QTableWidget,
    QHeaderView, QLabel, QTableWidgetItem)
from PyQt5.QtCore import Qt

from custom_widgets import (SimpleFilterArtistsTable,
    SongDataTableWidget, WidgetGroupBox)
from popups import NewPlaylistDialog
from style import (PlaylistSongsStyle, SimpleFilterPlaylistStyle,
    AdvFilterPlaylistStyle, QueueMakerStyle, CurrentQueueStyle)


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
        self.songs_table = SongDataTableWidget(True, True, self)
        self.songs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.songs_table.setFocusPolicy(Qt.NoFocus)

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

        self.setStyleSheet(PlaylistSongsStyle)

    def add_songs(self, pl_id):
        """
        Gets the songs, from the currently selected playlist and adds them to
        the table

        Parameters:
        pl_id - The ID of the playlist
        """
        songs = self.user.get_playlist_songs(pl_id)
        self.songs_table.add_songs(songs, False)


class AdvFilterPlaylistsUI(QWidget):
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
        self.songs_table = SongDataTableWidget(False, False, self)
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

        self.setStyleSheet(AdvFilterPlaylistStyle)

    def get_layout_data(self):
        """
        From the data inputted on this tab, get the data in a proper format
        to pass along to self.user.filter_playlist. If there are overlaps
        (i.e. two ANDs for a single playlist or artist_or's), then they are
        combined/concatenated
        """
        # Parse the layouts for the data and put into a dict
        filt_dict = self._parse_filt_layout()

        # Remove the empty logics, the ones without any filtering keywords
        for playlist, data in filt_dict.items():
            for logic in ['_and', '_or']:
                if len(data[logic]) == 1:
                    filt_dict[playlist].pop(logic)

        filt_songs = []
        # Run through each playlist and filter them
        for playlist, data in filt_dict.items():
            songs = self.user.get_playlist_songs(
                self.user.pl_ids[self.user.playlists.index(playlist)])
            filt_songs += self.user.filter_playlist(songs, _or=data)

        # Add songs to the table
        self.songs_table.add_songs(filt_songs, True)

    def _parse_filt_layout(self, layout=None, depth=0, filt_dict=None, pl=None,
                           logic=None):
        """
        Recursively queries the data from this tab to filter the playlist(s)
        selected. The arguments are used for the recursive-ness.

        This works since each important part of the layout is a separate and
        nested layout. So there's the parent one. Then a playlist layout, a
        nested logic layout and a nested (in the logic layout) filter layout.
        Playlist just means the name of the playlist. Logic is whether it's
        an AND or an OR. And filter is the filter choice of which there are
        seven described under User.filter_playlist. These are stored in a
        dictionary passed along which is returned at the end.

        Parameters:
        layout - (default None) The layout to parse as described above
        depth - (default 0) The number of times the method has been recursively
                called which allows us to know what Combobox has been reached
        filt_dict - (default None) The main dictionary that stores all of the
                    parsed data
        pl - (default None) The last playlist name used so that it can
                    be called in the dictionary for adding data
        logic - (default None) The last type of logic used like latest_pl
        """
        # Get the current layout and dictionary or new ones if first pass
        layout = layout or self.filt_layout
        filt_dict = filt_dict or {}

        # Iterate through the widgets/layouts of the current layout
        for ind in range(layout.count()):
            item = layout.itemAt(ind)

            # If the item is a widget...
            if isinstance(item, QWidgetItem):
                widget = item.widget()

                # And if it's a custom groupbox...
                if isinstance(widget, WidgetGroupBox):
                    # Get whether it's an AND or OR if there
                    if widget.widget_type == 'QCheckBox':
                        logic = '_or' if widget.groupbox.title() == 'OR' else '_and'
                        # Add the choice for 'NOT-ing' the logic
                        filt_dict[pl][logic]['_not'] = widget.title_widget.isChecked()

                    # Recursively run function with the current data 
                    filt_dict = self._parse_filt_layout(widget.groupbox.layout(),
                        depth=depth + 1, filt_dict=filt_dict, pl=pl, logic=logic)
                # And if it's a combobox...
                elif isinstance(widget, QComboBox):
                    # Depth 1 is the playlist name, so add that to the dict
                    if depth == 1:
                        filt_dict[widget.currentText()] = {'_and': {}, '_or': {}}
                        # Store current playlist name being filled in
                        pl = widget.currentText()
                    # Depth 4 has the filter type, so add that
                    elif depth == 4:
                        filt_dict[pl][logic][widget.currentText()] = ''
                        # Store current filter type
                        filt = widget.currentText()
                # And if it's a lineedit...
                elif isinstance(widget, QLineEdit):
                    # Comma-separate text into a list for filter choice
                    filt_dict[pl][logic][filt] = list(map(lambda x: x.strip(), widget.displayText().split(',')))
            # Or if the item is a layout...
            elif isinstance(item, QGridLayout):
                # Run recursively with current data
                filt_dict = self._parse_filt_layout(item, depth=depth + 1,
                    filt_dict=filt_dict, pl=pl, logic=logic)

        return filt_dict

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
        pl_group_box = WidgetGroupBox('Playlist', 'QPushButton', 'Remove', 370, pl_grid)

        # Button click to add a new logic ComboBox
        add_logic.clicked.connect(lambda: self.add_logic(pl_grid))
        # Button click to remove current playlist
        pl_group_box.title_widget.clicked.connect(lambda: pl_group_box.deleteLater())

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
        logic_group_box = WidgetGroupBox('Logic', 'QPushButton', 'Remove', 320, logic_grid)

        # Remove button for logic Groupbox removes it
        logic_group_box.title_widget.clicked.connect(lambda: logic_group_box.deleteLater())

        # Create grid layout for the AND logic section
        and_grid = QGridLayout()
        # Create groupbox for AND section
        and_group_box = WidgetGroupBox('AND', 'QCheckBox', 'Not', 365, and_grid)
        # Add the groupbox to the grid layout for the entire logic section
        logic_grid.addWidget(and_group_box, logic_grid.count(), 0)
        # Create button to add filters, add the functionality and add to layout
        and_add_filter = QPushButton('Add Filter')
        and_add_filter.clicked.connect(lambda: self.add_filter(and_grid))
        and_grid.addWidget(and_add_filter, 1000, 0)

        # Create grid layout for the OR logic section
        or_grid = QGridLayout()
        # Create groupbox for OR section
        or_group_box = WidgetGroupBox('OR', 'QCheckBox', 'Not', 365, or_grid)
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


class SimpleFilterPlaylistUI(QWidget):
    ADD_PLAYLIST_WIDTH = 500

    def __init__(self, parent, user, max_height, max_width):
        super().__init__(parent)
        self.max_height = max_height
        self.max_width = max_width

        # Bool used to not add artist when index change of artist Combobox is
        # cause by the change in the playlist Combobox
        self.do_not_add_artist = True

        self.user = user
        self.init_ui()

        self.commit.clicked.connect(self.add_artists_songs)

    def init_ui(self):
        # Table of artists to include/exclude
        self.artists_table = SimpleFilterArtistsTable(0, 1, self)
        self.artists_table.setHorizontalHeaderLabels(['Artists'])
        header = self.artists_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Combobox of the unique artists in the playlists Combobox
        self.artists = QComboBox()
        self.artists.setFixedWidth(self.ADD_PLAYLIST_WIDTH)
        # Add artist selected to table self.artists_table
        self.artists.currentIndexChanged.connect(self.add_artists)

        # Playlists Combobox like in PlaylistSongsUI
        self.playlists = QComboBox()
        self.playlists.addItems(self.user.playlists)
        self.playlists.setFixedWidth(self.ADD_PLAYLIST_WIDTH)
        # Get the artists of this playlist
        self.playlists.currentIndexChanged.connect(
            lambda: self.get_unique_artists(
                self.user.pl_ids[self.playlists.currentIndex()]))

        # Initialize for self.artists
        self.get_unique_artists(self.user.pl_ids[self.playlists.currentIndex()])
        # Combobox choice for including or excluding
        self.logic = QComboBox()
        self.logic.addItems(['Include', 'Exclude'])
        self.logic_text = QLabel('the following artists:')
        # Button to show what songs are return by total filter
        self.commit = QPushButton('Commit', self)
        self.commit.setMaximumWidth(self.max_width / 4)
        # Create button to add songs to queue
        self.add_songs_button = QPushButton('Add', self)
        self.add_songs_button.setMaximumWidth(self.max_width / 4)
        # Table to show filtered songs
        self.songs_table = SongDataTableWidget(False, False, self)
        self.songs_table.setMaximumWidth(self.max_width - self.ADD_PLAYLIST_WIDTH)

        # Total layout for left side
        h_box_logic = QHBoxLayout()
        h_box_logic.addWidget(self.logic)
        h_box_logic.addWidget(self.logic_text)
        h_box_logic.addStretch()
        self.filt_layout = QGridLayout()
        self.filt_layout.addWidget(self.playlists, 0, 1)
        self.filt_layout.addWidget(self.artists, 1, 1)
        self.filt_layout.addLayout(h_box_logic, 2, 1)
        self.filt_layout.addWidget(self.artists_table, 3, 1)

        # Total layout for right side
        h_box_buttons = QHBoxLayout()
        h_box_buttons.addWidget(self.add_songs_button)
        h_box_buttons.addWidget(self.commit)
        v_box_right = QVBoxLayout()
        v_box_right.addLayout(h_box_buttons)
        v_box_right.addWidget(self.songs_table)

        # Put it all together
        h_box = QHBoxLayout(self)
        h_box.addLayout(self.filt_layout)
        h_box.addLayout(v_box_right)

        self.setStyleSheet(SimpleFilterPlaylistStyle)

    @property
    def artists_set(self):
        """
        A list of the artists in self.artists_table
        """
        return set(self.artists_table.item(x, 0).text()
            for x in range(self.artists_table.rowCount()))

    def get_unique_artists(self, pl_id):
        """
        Gets every different artist for the playlist currently selected in the
        self.playlists Combobox
        """
        # The change in playlist causes a change in the artist which triggers
        # adding the artist to the table, so prevent the first time
        self.do_not_add_artist = True

        # Add the unique artists to Combobox
        unique_artists = set()
        self.songs = self.user.get_playlist_songs(pl_id)
        for song in self.songs:
            for artist in song[1]:
                unique_artists.add(artist)

        # Clear Combobox and add new artists alphabetically
        self.artists.clear()
        # Reset bool since clearing Combobox changes current index :/
        self.do_not_add_artist = True
        self.artists.addItems(sorted(list(unique_artists)))

        # Reset artists table by deleting ever row
        for _ in range(self.artists_table.rowCount()):
            self.artists_table.removeRow(0)

    def add_artists(self):
        """
        Adds the selected artist from the self.artists Combobox and adds it
        to the self.artists_table table widget.
        """
        # Doesn't add if caused by change in playlist
        if not self.do_not_add_artist:
            artist = self.artists.currentText()
            cur_row = self.artists_table.rowCount()
            # Don't add if already in list
            if artist not in self.artists_set:
                self.artists_table.insertRow(cur_row)
                self.artists_table.setItem(cur_row, 0, QTableWidgetItem(artist))

        self.do_not_add_artist = False

    def add_artists_songs(self):
        """
        Adds all the songs by every artist in the self.artists_table table
        widget if the self.logic Combobox is 'Include' or adds all the songs
        not by the artists in the table widget if self.logic is 'Exclude'.
        """
        logic = self.logic.currentText()
        songs_to_add = []

        # Run through every song in the current playlist selected
        for song in self.songs:
            # Since some songs have multiple artists
            for artist in song[1]:
                if (artist in self.artists_set and logic == 'Include') or \
                   (artist not in self.artists_set and logic == 'Exclude'):
                    songs_to_add.append(song)
        self.songs_table.add_songs(songs_to_add, True)


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
        self.queue_list = SongDataTableWidget(False, False, self)

        # Put it all together
        v_box = QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.create_playlist)
        v_box.addWidget(self.clear_songs)
        v_box.addWidget(self.create_songs)

        h_box = QHBoxLayout(self)
        h_box.addLayout(v_box)
        h_box.addWidget(self.queue_list)

        self.setStyleSheet(QueueMakerStyle)

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
        self.current_queue = SongDataTableWidget(False, False, self)

        v_box = QVBoxLayout(self)
        v_box.addWidget(self.current_queue)

        self.setStyleSheet(CurrentQueueStyle)
