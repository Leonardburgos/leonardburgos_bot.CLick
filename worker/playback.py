from PyQt6.QtCore import QThread, pyqtSignal
from .recorder import Recorder

class PlaybackThread(QThread):
    playback_complete = pyqtSignal()  # Signal emitted when playback is complete
    playback_started = pyqtSignal()   # Signal emitted when playback starts
    playback_stopped = pyqtSignal()   # Signal emitted when playback is stopped

    def __init__(self, recorder, repeat_count: int, delay_after_playback: float, repeat_indefinitely: bool):
        super().__init__()
        self.recorder = recorder
        self.repeat_count = repeat_count
        self.delay_after_playback = delay_after_playback
        self.repeat_indefinitely = repeat_indefinitely

    def run(self):
        self.playback_started.emit()  # Emit the signal that playback has started
        self.recorder.play_events(self.repeat_count, self.delay_after_playback, self.repeat_indefinitely)
        self.playback_complete.emit()  # Emit the signal once playback is finished

    def stop(self):
        """Stop the playback thread safely and immediately."""
        self.recorder.stop_playing()
        self.quit()  # Stop the thread if it's in a blocked state
        self.wait()  # Wait for the thread to exit the run method completely
        self.playback_stopped.emit()  # Emit the signal once playback is stopped
