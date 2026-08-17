import os
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class ExportFileHandler(PatternMatchingEventHandler):
    def __init__(self, callback, patterns):
        super().__init__(patterns=patterns, ignore_directories=True, case_sensitive=False)
        self.callback = callback
        self.last_processed = {}

    def on_created(self, event):
        self._process_event(event)

    def on_modified(self, event):
        self._process_event(event)

    def _process_event(self, event):
        filepath = event.src_path
        
        # Avoid double-processing within a short time window (de-duplication)
        current_time = time.time()
        if filepath in self.last_processed:
            if current_time - self.last_processed[filepath] < 2.0:
                return
        
        self.last_processed[filepath] = current_time

        # Wait a tiny bit (1.5 seconds) to ensure the game has finished saving/writing the file
        time.sleep(1.5)
        
        # Trigger the callback
        if os.path.exists(filepath):
            self.callback(filepath)

class ExportWatcher:
    def __init__(self, watch_dir, callback):
        self.watch_dir = watch_dir
        self.callback = callback
        self.observer = None

    def start(self):
        """
        Starts the directory watcher in a background thread.
        """
        if self.observer:
            return

        # Ensure watch directory exists
        os.makedirs(self.watch_dir, exist_ok=True)

        event_handler = ExportFileHandler(
            callback=self.callback,
            patterns=["*.rtf", "*.html", "*.htm", "*.txt", "*.csv"]
        )
        
        self.observer = Observer()
        self.observer.schedule(event_handler, path=self.watch_dir, recursive=False)
        self.observer.start()

    def stop(self):
        """
        Stops the directory watcher thread.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
