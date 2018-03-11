# Allows for import of client.py
from inspect import getsourcefile
import os.path as path, sys
cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
par_dir = cur_dir[:cur_dir.rfind(path.sep)]
gpar_dir = par_dir[:par_dir.rfind(path.sep)]
sys.path.insert(0, par_dir)

from PyQt5.QtWidgets import (QPushButton, QLineEdit, QHBoxLayout, QDialog, 
    QDialog, QDialogButtonBox, QLabel, QCheckBox, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt

from client import Client
# After import, remove from path and no one is the wiser
sys.path.pop(0)

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
        self.button.clicked.connect(self.accept)
        self.input = QLineEdit()
        self.input.setText('chester_mccrumpet')

        # Design the GUI
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.input)
        h_box.addWidget(self.button)
        h_box.addStretch()

        self.setLayout(h_box)
        self.setWindowTitle('Spearch')

    def accept(self):
        """
        Login with text in the input. This creates a Client object which starts
        up the Spotify login. That's where the password is typed.
        """
        self.client = Client(self.input.text(), SCOPE,
                             path.join(gpar_dir, 'client.ini'),
                             path.join(gpar_dir, 'geckodriver.exe'))
        # Added to give a correct return from exec_()
        super().accept()


class NewPlaylistDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Playlist Name')

        # Header
        header = QLabel('New Playlist Name')
        # Line Edit for playlist name
        self.playlist_name = QLineEdit()
        # Checkbox for private playlist
        self.private = QCheckBox()
        # Checkbox description
        private_desc = QLabel('Check for private playlist')
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        h_box = QHBoxLayout()
        h_box.addWidget(self.private)
        h_box.addWidget(private_desc)
        h_box.addStretch()

        # Add it all together
        layout = QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(self.playlist_name)
        layout.addLayout(h_box)
        # layout.addWidget(self.private)
        layout.addWidget(buttons)

    @staticmethod
    def getPlaylistName():
        dialog = NewPlaylistDialog()
        result = dialog.exec_()

        playlist_name = dialog.playlist_name.text()
        is_private = dialog.private.isChecked()
        ok = result == QDialog.Accepted
        return playlist_name, is_private, ok