try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None
    PatternMatchingEventHandler = object

class ExportFileHandler(PatternMatchingEventHandler if HAS_WATCHDOG else object):
    def __init__(self, callback, patterns):
        if HAS_WATCHDOG:
            super().__init__(patterns=patterns, ignore_directories=True, case_sensitive=False)
        self.callback = callback
        self.last_processed = {}

    def on_created(self, event):
        self._process_event(event)

    def on_modified(self, event):
        self._process_event(event)

    def _process_event(self, event):
        filepath = getattr(event, "src_path", event)
        
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
        self._stop_event = None
        self._poll_thread = None

    def start(self):
        """
        Starts the directory watcher in a background thread.
        """
        if self.observer or (self._poll_thread and self._poll_thread.is_alive()):
            return

        # Ensure watch directory exists
        os.makedirs(self.watch_dir, exist_ok=True)

        if HAS_WATCHDOG and Observer is not None:
            event_handler = ExportFileHandler(
                callback=self.callback,
                patterns=["*.rtf", "*.html", "*.htm", "*.txt", "*.csv"]
            )
            
            self.observer = Observer()
            # Recursive: the FM26 export plugin writes into a nested
            # "FM26PlayerExport by vinteset" subfolder, so subdirectories must be
            # watched too (harmless for FM24 flat exports).
            self.observer.schedule(event_handler, path=self.watch_dir, recursive=True)
            self.observer.start()
        else:
            # Fallback polling watcher when watchdog is not installed
            import threading
            self._stop_event = threading.Event()
            valid_exts = {".rtf", ".html", ".htm", ".txt", ".csv"}
            known_mtimes = {}

            def _poll():
                while not self._stop_event.is_set():
                    try:
                        for root, _, files in os.walk(self.watch_dir):
                            for fname in files:
                                if os.path.splitext(fname)[1].lower() in valid_exts:
                                    fpath = os.path.join(root, fname)
                                    try:
                                        mtime = os.path.getmtime(fpath)
                                        if fpath not in known_mtimes:
                                            known_mtimes[fpath] = mtime
                                        elif mtime > known_mtimes[fpath]:
                                            known_mtimes[fpath] = mtime
                                            time.sleep(1.5)
                                            if os.path.exists(fpath):
                                                self.callback(fpath)
                                    except OSError:
                                        pass
                    except Exception:
                        pass
                    self._stop_event.wait(2.0)

            self._poll_thread = threading.Thread(target=_poll, daemon=True)
            self._poll_thread.start()

    def stop(self):
        """
        Stops the directory watcher thread.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        if self._stop_event:
            self._stop_event.set()
            if self._poll_thread:
                self._poll_thread.join(timeout=1.0)
            self._stop_event = None
            self._poll_thread = None
