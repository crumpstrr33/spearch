import sys

from PyQt5.QtWidgets import QApplication

from main_window import Window
from login import Login


def main():
    app = QApplication(sys.argv)

    # Login
    login = Login()
    login.exec_()

    # Do actual stuff
    window = Window(login.client)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
