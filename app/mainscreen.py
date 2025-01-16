import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout, QCheckBox, QFileDialog
from PyQt6.QtGui import QPixmap, QIcon
from plyer import notification
from pynput import keyboard
from worker import Recorder, PlaybackThread
from forms import MainWindow
from .directory import DirectoryPath
from PyQt6.QtCore import pyqtSignal
import os
import json

class MainWindow(QMainWindow, MainWindow):  
    # Define signals
    playback_started = pyqtSignal()  # Signal for playback start
    playback_stopped = pyqtSignal()  # Signal for playback stop
    playback_complete = pyqtSignal()  # Signal for playback completion
    save_signal = pyqtSignal(dict)  # Signal to trigger the save method

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('bot.Click by John Leonard Burgos')
        self.setWindowIcon(QIcon("assets/window.png"))
        self.setStyleSheet("""
            QMainWindow {background-color: #F0F0F0; /* Light mode background */
            }
            QLabel, QPushButton, QLineEdit, QCheckBox {
            color: #000000; /* Set text color to black */
            }
            QPushButton {
            background-color: #ffa6f1; /* Optional: light gray for buttons */
            border: 1px solid #A0A0A0;
            width: 10px; /* Optional: subtle border for buttons */
            }
            QLineEdit {
            background-color: #FFFFFF; /* White background for input fields */
            border: 1px solid #A0A0A0; /* Subtle border for input fields */
            }
            QCheckBox {
            spacing: 5px; /* Optional: spacing between checkbox and label */
            }
        """)
        self.setFixedSize(500, 400)
        self.playback_thread = None
        self.recorder = Recorder(on_playback_complete=self.on_playback_complete, save_signal=self.save_signal)

        # Initialize the filename variable
        self.imported_file = None

        main_layout = QVBoxLayout()



        # Logo and title
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        
        botcli_pixmap = QPixmap("assets/botclick.png")
        botcli_label = QLabel()
        botcli_label.setPixmap(botcli_pixmap.scaled(150, 150)) 
        logo_layout.addWidget(botcli_label)
    
        logo_layout.addStretch()
        main_layout.addLayout(logo_layout)

        # Shortcut keys information
        shortcut_info = QLabel(
            "Shortcut Keys:\n"
            "F10: Start/Stop Recording\n"
            "Ctrl+F2: Start/Stop Playing"
        )
        main_layout.addWidget(shortcut_info)

        self.status_label = QLabel('Status: Idle')
        main_layout.addWidget(self.status_label)

        self.record_button = QPushButton('Start Recording')
        self.record_button.clicked.connect(self.start_recording)
        main_layout.addWidget(self.record_button)

        self.stop_button = QPushButton('Stop Recording')
        self.stop_button.clicked.connect(self.stop_recording)
        main_layout.addWidget(self.stop_button)

        self.play_button = QPushButton('Play Recording')
        self.play_button.clicked.connect(self.start_playing)
        main_layout.addWidget(self.play_button)

        self.stop_playing_button = QPushButton('Stop Playing')
        self.stop_playing_button.clicked.connect(self.stop_playing)
        main_layout.addWidget(self.stop_playing_button)

        self.repeat_input = QLineEdit(self)
        self.repeat_input.setPlaceholderText("Repeat count (default 1)")
        main_layout.addWidget(self.repeat_input)

        self.delay_input = QLineEdit(self)
        self.delay_input.setPlaceholderText("Delay after playback (seconds)")
        main_layout.addWidget(self.delay_input)

        self.repeat_indefinitely_checkbox = QCheckBox("Repeat indefinitely")
        self.repeat_indefinitely_checkbox.setChecked(True)  # Set default as checked
        self.repeat_indefinitely_checkbox.stateChanged.connect(self.toggle_repeat_input)
        main_layout.addWidget(self.repeat_indefinitely_checkbox)

        # File import/remove section
        self.import_button = QPushButton('Import Recording')
        self.import_button.clicked.connect(self.import_recording)
        main_layout.addWidget(self.import_button)

        self.remove_button = QPushButton('Remove Imported File')
        self.remove_button.clicked.connect(self.remove_file)
        self.remove_button.setDisabled(True)  # Initially disabled
        main_layout.addWidget(self.remove_button)

        self.filename_label = QLabel("No file imported")
        main_layout.addWidget(self.filename_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Key listener setup
        self.ctrl_pressed = False
        self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.listener.start()

        self.toggle_repeat_input()

        # Connect the signals to methods
        self.playback_started.connect(self.on_playback_started)
        self.playback_stopped.connect(self.on_playback_stopped)
        self.playback_complete.connect(self.on_playback_complete)
        self.save_signal.connect(self.handle_save_events)

    def toggle_repeat_input(self):
        if self.repeat_indefinitely_checkbox.isChecked():
            self.repeat_input.setDisabled(True)
        else:
            self.repeat_input.setEnabled(True)

    def handle_save_events(self, events):
 
    # Instantiate the DirectoryPath class to get the directory path
        directory_path = DirectoryPath()
        base_name = "record"  # Base name for the file
        extension = ".json"  # File extension

    # Generate a unique filename
        file_path = directory_path.generate_unique_filename(base_name, extension)
    
    # Save the events to the file
        with open(file_path, 'w') as f:
            json.dump(events, f, indent=4)

        print(f"Recording saved to {file_path}")

    # After saving, auto-import the saved file and set it as the active file
        self.imported_file = file_path
        self.filename_label.setText(f"Imported File: {os.path.basename(file_path)}")
        self.remove_button.setEnabled(True)  # Enable remove button
        self.record_button.setDisabled(True)  # Disable record button

    def import_recording(self):
        """
        This method will allow the user to import a JSON file.
        It will load the file, set the filename label, and disable the recording button.
        """
        # Use QFileDialog.getOpenFileName directly without Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Recording File", "", "JSON Files (*.json);;All Files (*)")
    
        if file_path:
            self.imported_file = file_path
            self.filename_label.setText(f"Imported File: {os.path.basename(file_path)}")
            self.record_button.setDisabled(True)  # Disable the record button
            self.remove_button.setEnabled(True)  # Enable the remove button
            # Load the file and process the events into the recorder
            with open(file_path, 'r') as f:
                events = json.load(f)
                self.recorder.events = events  # Assume this sets the events for playback
                print(f"Recording from {file_path} imported successfully.")


    def remove_file(self):
        """
        This method will remove the imported file and enable the recording button again.
        """
        self.imported_file = None
        self.filename_label.setText("No file imported")
        self.record_button.setEnabled(True)  # Enable the record button again
        self.remove_button.setDisabled(True)  # Disable the remove button
        self.recorder.events = {}  # Clear the loaded events
        print("Imported file removed.")

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.f10:
                if self.recorder.is_recording:
                    self.stop_recording()
                else:
                    self.start_recording()
            elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.f2 and self.ctrl_pressed:
                if self.recorder.is_playing:
                    self.stop_playing()
                elif not self.recorder.is_recording:  # Prevent playing if recording is active
                    self.start_playing()
        except AttributeError:
            pass

    def on_key_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False

    def on_playback_started(self):
        self.status_label.setText('Status: Playing...')

    def on_playback_stopped(self):
        self.status_label.setText('Status: Playback Stopped')

    def on_playback_complete(self):
        if not self.repeat_indefinitely_checkbox.isChecked():
            notification.notify(
                title='Playing Complete',
                message='The playback has completed.',
                timeout=0.5
            )
            self.status_label.setText('Status: Playing Complete')
            self.repeat_input.setEnabled(True)
            self.delay_input.setEnabled(True)
            self.play_button.setEnabled(True)
            self.record_button.setEnabled(True)
        else:
            self.status_label.setText('Status: Playing... (Repeating Indefinitely)')

    def start_recording(self):
        if self.recorder.is_playing or self.imported_file:
            return  # Prevent recording if already playing or file is imported

        self.play_button.setDisabled(True)
        notification.notify(
            title='Recording Started',
            message='Recording Started. Press F10 to stop.',
            timeout=0.5
        )
        self.status_label.setText('Status: Recording...')
        self.recorder.start_recording()

    def stop_recording(self):
        notification.notify(
            title='Recording Stopped',
            message='Recording Stopped.',
            timeout=0.5
        )
        self.status_label.setText('Status: Recording Stopped')
        self.play_button.setEnabled(True)
        self.record_button.setEnabled(True)
        self.recorder.stop_recording()

    def start_playing(self):
        if self.recorder.is_recording:
            notification.notify(
                title='Cannot Start Playback',
                message='Stop the recording before starting playback.',
                timeout=0.5
            )
            return
        self.record_button.setDisabled(True)
        self.play_button.setDisabled(True)  # Disable play button during playback
        notification.notify(
            title='Playing Started',
            message='Playing the recorded actions...',
            timeout=0.5
        )
        self.status_label.setText('Status: Playing...')
        self.repeat_input.setDisabled(True)
        self.delay_input.setDisabled(True)

        # Get repeat count and delay after playback
        try:
            repeat_count = int(self.repeat_input.text()) if self.repeat_input.text() else 1
            delay_after_playback = float(self.delay_input.text()) if self.delay_input.text() else 0
        except ValueError:
            self.status_label.setText('Status: Invalid input for repeat or delay')
            return

        repeat_indefinitely = self.repeat_indefinitely_checkbox.isChecked()
        self.playback_thread = PlaybackThread(
            self.recorder, repeat_count, delay_after_playback, repeat_indefinitely
        )

        self.playback_thread.playback_started.connect(self.on_playback_started)
        self.playback_thread.playback_complete.connect(self.on_playback_complete)
        self.playback_thread.playback_stopped.connect(self.on_playback_stopped)
        # Start the playback thread
        self.playback_thread.start()

    def stop_playing(self):
        if self.playback_thread is not None:
            self.playback_thread.stop()

        notification.notify(
            title='Playing Stopped',
            message='Playing Stopped.',
            timeout=0.5
        )
        self.recorder.stop_playing()
        self.play_button.setEnabled(True)
        self.record_button.setEnabled(True)
        self.repeat_input.setEnabled(True)
        self.delay_input.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
