import logging
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class DirectoryWatcher(FileSystemEventHandler):
    def __init__(self, path: str, on_new_file):
        """
        :param path: directory path to watch
        :param on_new_file: callback function(file_path: str)
        """
        self.path = path
        self.on_new_file = on_new_file
        self.observer = Observer()

    def on_created(self, event):
        """Triggered when a file or folder is created."""
        if not event.is_directory:
            self.on_new_file(event.src_path)

    def start(self):
        """Start watching the directory."""
        # Handle already existing files
        for filename in os.listdir(self.path):
            filepath = os.path.join(self.path, filename)
            if os.path.isfile(filepath):
                self.on_new_file(filepath)

        self.observer.schedule(self, self.path, recursive=False)
        self.observer.start()
        logging.info(f"Started watching: {self.path}")

    def stop(self):
        """Stop watching."""
        self.observer.stop()
        self.observer.join()
        logging.info(f"Stopped watching: {self.path}")
