# Allows for import of client.py
from inspect import getsourcefile
import os.path as path, sys
cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
par_dir = cur_dir[:cur_dir.rfind(path.sep)]
gpar_dir = par_dir[:par_dir.rfind(path.sep)]
sys.path.insert(0, par_dir)

from PyQt5.QtWidgets import QPushButton, QLineEdit, QHBoxLayout, QDialog

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
        self.button.clicked.connect(self.login)
        self.input = QLineEdit()

        # Design the GUI
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.input)
        h_box.addWidget(self.button)
        h_box.addStretch()

        self.setLayout(h_box)
        self.setWindowTitle('Spearch')

    def login(self):
        """
        Login with text in the input. This creates a Client object which starts
        up the Spotify login. That's where the password is typed.
        """
        print(gpar_dir)
        self.client = Client(self.input.text(), SCOPE,
                             path.join(gpar_dir, 'client.ini'))
        self.close()
