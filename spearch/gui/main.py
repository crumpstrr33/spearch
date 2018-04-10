import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from main_window import Window
from popups import Login

INIT_WIDTH = 1080
INIT_HEIGHT = 720

def main():
    """
    Main app. If the window is exited by loggin in as a new user, then the
    while loop scope will repeat and log in as the new user and delete the old
    window, app and all.
    """
    current_exit_code = Window.NEW_USER_EXIT_CODE
    init = True
    # Loops if the exit code is by the new user code
    while current_exit_code == Window.NEW_USER_EXIT_CODE:
        app = QApplication(sys.argv)

        # Only initially get the login this way
        if init:
            login = Login()
            login.exec_()

            client = login.client

        screen_size = QDesktopWidget().screenGeometry()
        window = Window(client, screen_size.height(), screen_size.width())
        window.resize(INIT_WIDTH, INIT_HEIGHT)
        window.show()

        # Gets the exit code for when app is exited
        current_exit_code = app.exec_()
        # Get the Client object from this new login
        client = window.client

        # Delete the QApplication object
        app = None
        # No need to initialize the login window
        init = False


if __name__ == "__main__":
    main()
