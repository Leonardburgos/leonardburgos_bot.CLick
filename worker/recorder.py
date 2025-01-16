import sys
import json
import os
import time
from pynput import mouse, keyboard
from threading import Event
from PyQt6.QtWidgets import QFileDialog

class Recorder:
    def __init__(self, on_playback_complete=None, save_signal=None):
        self.events = {}
        self.is_recording = False
        self.is_playing = False
        self.on_playback_complete = on_playback_complete
        self.save_signal = save_signal  # The save signal to notify main thread
        self.repeat_count = 1
        self.delay_after_playback = 0
        self.stop_playback_flag = Event()  # Using threading Event for synchronization
        self.event_counter = 0

        # Define key mapping for key deserialization
        self.KEY_MAPPING = {
            'Key.f1': keyboard.Key.f1,
            'Key.f2': keyboard.Key.f2,
            'Key.f3': keyboard.Key.f3,
            'Key.f4': keyboard.Key.f4,
            'Key.f5': keyboard.Key.f5,
            'Key.f6': keyboard.Key.f6,
            'Key.f7': keyboard.Key.f7,
            'Key.f8': keyboard.Key.f8,
            'Key.f9': keyboard.Key.f9,
            'Key.f10': keyboard.Key.f10,
            'Key.f11': keyboard.Key.f11,
            'Key.f12': keyboard.Key.f12,

            'Key.ctrl_l': keyboard.Key.ctrl_l,
            'Key.ctrl_r': keyboard.Key.ctrl_r,
            'Key.shift_l': keyboard.Key.shift,
            'Key.shift_l': keyboard.Key.shift_l,
            'Key.shift_r': keyboard.Key.shift_r,
            'Key.alt_l': keyboard.Key.alt_l,
            'Key.alt_r': keyboard.Key.alt_r,
            'Key.cmd': keyboard.Key.cmd,  # Windows key, Command key on macOS
            'Key.backspace': keyboard.Key.backspace,
            'Key.tab': keyboard.Key.tab,
            'Key.enter': keyboard.Key.enter,
            'Key.esc': keyboard.Key.esc,
            'Key.space': keyboard.Key.space,
            'Key.left': keyboard.Key.left,
            'Key.right': keyboard.Key.right,
            'Key.up': keyboard.Key.up,
            'Key.down': keyboard.Key.down,
            'Key.insert': keyboard.Key.insert,
            'Key.delete': keyboard.Key.delete,
            'Key.home': keyboard.Key.home,
            'Key.end': keyboard.Key.end,
            'Key.page_up': keyboard.Key.page_up,
            'Key.page_down': keyboard.Key.page_down,

            'Key.caps_lock': keyboard.Key.caps_lock,
            'Key.num_lock': keyboard.Key.num_lock,
            'Key.scroll_lock': keyboard.Key.scroll_lock,
            'Key.pause': keyboard.Key.pause,

            'Key.print_screen': keyboard.Key.print_screen,
            # For num pad keys, use KeyCode objects:
            'num_pad_0': keyboard.KeyCode.from_char('0'),
            'num_pad_1': keyboard.KeyCode.from_char('1'),
            'num_pad_2': keyboard.KeyCode.from_char('2'),
            'num_pad_3': keyboard.KeyCode.from_char('3'),
            'num_pad_4': keyboard.KeyCode.from_char('4'),
            'num_pad_5': keyboard.KeyCode.from_char('5'),
            'num_pad_6': keyboard.KeyCode.from_char('6'),
            'num_pad_7': keyboard.KeyCode.from_char('7'),
            'num_pad_8': keyboard.KeyCode.from_char('8'),
            'num_pad_9': keyboard.KeyCode.from_char('9'),
            'num_pad_add': keyboard.KeyCode.from_char('+'),
            'num_pad_subtract': keyboard.KeyCode.from_char('-'),
            'num_pad_multiply': keyboard.KeyCode.from_char('*'),
            'num_pad_divide': keyboard.KeyCode.from_char('/'),
            'num_pad_enter': keyboard.Key.enter,  # This can be treated as the Enter key
        }
    
        self.MOUSE_BUTTON_MAPPING = {
            'Button.left': mouse.Button.left,
            'Button.right': mouse.Button.right,
            'Button.middle': mouse.Button.middle,
        }


    def _generate_event_key(self):
        self.event_counter += 1
        return self.event_counter

    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            event_key = self._generate_event_key()
            event = ('mouse_click', time.time(), x, y, str(button), pressed)  # Convert button to string
            self.events[event_key] = event

    def on_move(self, x, y):
        try:
            if self.is_recording:
                event_key = self._generate_event_key()
                event = ('mouse_move', time.time(), x, y)
                self.events[event_key] = event
        except Exception as e:
            print(f"Error in callback: {e}")

    def on_scroll(self, x, y, dx, dy):
        if self.is_recording:
            event_key = self._generate_event_key()
            event = ('mouse_scroll', time.time(), x, y, dx, dy)
            self.events[event_key] = event

    def on_press(self, key):
        if self.is_recording:
            event_key = self._generate_event_key()

        # Check if the key is a printable character
            if hasattr(key, 'char') and key.char is not None:  # Printable character
                key_str = key.char  # Directly use the character itself (no quotes)
            else:  # Special key (e.g., Key.backspace)
                key_str = str(key)  # Store the name of the key (e.g., 'Key.backspace')

            event = ('key_press', time.time(), key_str)  # Store key as string
            self.events[event_key] = event

    def on_release(self, key):
        if self.is_recording:
            event_key = self._generate_event_key()

        # Check if the key is a printable character
            if hasattr(key, 'char') and key.char is not None:  # Printable character
                key_str = key.char  # Directly use the character itself (no quotes)
            else:  # Special key (e.g., Key.backspace)
                key_str = str(key)  # Store the name of the key (e.g., 'Key.backspace')

            event = ('key_release', time.time(), key_str)  # Store key as string
            self.events[event_key] = event

    def start_recording(self):
        self.events = {}
        self.is_recording = True
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        self.is_recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

        # Emit the save_signal to notify the main thread to open the save file dialog
        if self.save_signal:
            self.save_signal.emit(self.events)

    def save_events_to_file(self, events):
        """
        This method will be called by the main thread to show the file dialog and save events.
        """
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            None, "Save Recorded Events", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convert events to JSON
            events_json = self._convert_events_to_json(events)

            # Save events to the selected file path
            with open(file_path, 'w') as f:
                json.dump(events_json, f, indent=4)

            print(f"Recording saved to: {file_path}")
        else:
            print("File save was cancelled.")

    def _convert_events_to_json(self, events):
        """
        Convert events dictionary to a JSON-serializable format.
        """
        json_ready_events = {}
        for key, event in events.items():
            event_type, timestamp, *args = event
            # For key events, convert the key/button to string
            json_ready_events[key] = {
                'event_type': event_type,
                'timestamp': timestamp,
                'args': [str(arg) if isinstance(arg, (keyboard.Key, mouse.Button)) else arg for arg in args]
            }
        return json_ready_events

    def stop_playing(self):
        """
        Set the stop flag to halt playback.
        """
        print("Stopping playback...")
        self.stop_playback_flag.set()  # Trigger stop
        self.is_playing = False
    
    def play_events(self, repeat_count=1, delay_after_playback=0, repeat_indefinitely=False):
        if not self.events:
            print("No events to play.")
            return

        self.is_playing = True
        self.repeat_count = repeat_count
        self.delay_after_playback = delay_after_playback
        self.repeat_indefinitely = repeat_indefinitely
        self.stop_playback_flag.clear()  # Reset stop flag

        mouse_controller = mouse.Controller()
        keyboard_controller = keyboard.Controller()

        iteration = 0
        while self.repeat_indefinitely or iteration < self.repeat_count:
            iteration += 1

            if self.stop_playback_flag.is_set():  # Check if playback has been stopped
                print("Playback stopped.")
                break

            start_time = min(event[1] for event in self.events.values())  # Get the earliest event timestamp
            playback_start = time.time()

            for event_key, event in self.events.items():
                if self.stop_playback_flag.is_set():  # Check for stop flag on every event
                    print("Playback stopped during event processing.")
                    break

                event_time = event[1] - start_time  # Event time relative to the start of the recording
                current_time = time.time() - playback_start

                time_to_wait = event_time - current_time
                if time_to_wait > 0:
                    if time_to_wait > 3600:
                        time_to_wait = 3600  # Cap the wait time to a max of 1 hour
                    print(f"Waiting {time_to_wait:.2f} seconds before next event...")
                    self.stop_playback_flag.wait(time_to_wait)  # Wait with interruptibility

                event_type = event[0]
                args = event[2:]

                print(f"Executing event: {event_type} with arguments: {args}")  # Debugging output

                if event_type == 'mouse_move':
                    x, y = args
                    mouse_controller.position = (x, y)
                elif event_type == 'mouse_click':
                    x, y, button, pressed = args
                    mouse_controller.position = (x, y)
                    button = self.MOUSE_BUTTON_MAPPING.get(button, button)  # Convert button back to mouse.Button
                    if pressed:
                        mouse_controller.press(button)
                    else:
                        mouse_controller.release(button)
                elif event_type == 'mouse_scroll':
                    x, y, dx, dy = args
                    mouse_controller.position = (x, y)
                    mouse_controller.scroll(dx, dy)
                elif event_type == 'key_press' or event_type == 'key_release':
                    key = args[0]
                    if key.startswith('Key.'):
                        key = getattr(keyboard.Key, key.split('.')[1])   # Convert key back to keyboard.Key
                    keyboard_controller.press(key) if event_type == 'key_press' else keyboard_controller.release(key)
                elif event_type == 'key_release':
                    key = args[0]
                    key = self.KEY_MAPPING.get(key, key)  # Convert key back to keyboard.Key
                    keyboard_controller.release(key)

            if self.delay_after_playback > 0:
                self.stop_playback_flag.wait(self.delay_after_playback)

        self.is_playing = False
        if self.on_playback_complete:
            self.on_playback_complete()

    