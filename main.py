from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
import sys
from app import MainScreen

try:
    app = QApplication(sys.argv)
    mainpage = MainScreen()
    mainpage.show()

    sys.exit(app.exec())
except SystemExit:
    print("Closing windows....")
except Exception as e:
        print(f"Clossing windows with Errors: {e}")

       