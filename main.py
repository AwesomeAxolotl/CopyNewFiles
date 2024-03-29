# watches for new files in a directory and copies them to a target directory
# with incrementing file name

import logging
from watchdog.observers import Observer
from file_check import FileCheck

# edit:
cache_dir = r"C:/Users/.../AppData/Local/Mozilla/Firefox/Profiles/..."
target_dir = r"C:/OutputDir"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = FileCheck(target_dir, ["png", "jpg", "webp", "gif"], 301, 301, True)
    observer = Observer()
    observer.schedule(event_handler, cache_dir, recursive = False)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(0.10)
    finally:
        observer.stop()
        observer.join()