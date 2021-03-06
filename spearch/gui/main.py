from inspect import getsourcefile
import os.path as path, sys

cur_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))

from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtGui import QIcon

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
        app.setWindowIcon(
            QIcon(
                path.join(
                    cur_dir[: cur_dir.rfind(path.sep)], "icon", "spearch_icon.ico"
                )
            )
        )

        # Only initially get the login this way
        if init:
            login = Login()
            login.exec_()
            # If quit out of login window, then end loop
            try:
                client = login.client
            except:
                break

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
