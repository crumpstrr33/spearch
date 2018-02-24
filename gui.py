import sys

from PyQt5.QtWidgets import (QMainWindow, QDialog, QPushButton, QLineEdit,
    QHBoxLayout, QApplication, QWidget)

from client import Client
from user import User

SCOPE = 'user-modify-playback-state ' + \
        'playlist-read-private playlist-read-collaborative ' + \
        'playlist-modify-private playlist-modify-public '



class Window(QMainWindow):

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.user = User(self.client.access_token, self.client.token_birth)
        self.resize(600, 400)


class Login(QDialog):

    def __init__(self):
        super().__init__()
        self.button = QPushButton('Login', self)
        self.button.clicked.connect(self.login)
        self.input = QLineEdit()

        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.input)
        h_box.addWidget(self.button)
        h_box.addStretch()

        self.setLayout(h_box)
        self.setWindowTitle('Spearch')

    def login(self):
        self.client = Client(self.input.text(), SCOPE)
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = Window(login.client)
        window.show()

    sys.exit(app.exec_())
