from watchdog.events import FileSystemEvent, FileSystemEventHandler
from shutil import copy
from time import time
from magic import from_file
from pathlib import Path
import re

# watcher keeps the time the last file event happened on each file
# after the file sitting idle for 5 seconds it will be handled further

class FileCheck(FileSystemEventHandler):
    target_path = ""
    c = 1
    queue = []
    queue_cursor = 0
    file_type_re = re.compile("^\w+")
    image_size_re = re.compile("(\d+)\s?x\s?(\d+)")

    watcher = {}

    def __init__(self, _target_path, file_types: list, min_width: int = -1, 
                 min_height: int = -1, reset_counter_on_empty = False):
        super().__init__()
        self.wait_timer = 5
        self.min_width = min_width
        self.min_height = min_height
        self.file_types = file_types
        self.limit_dimensions = min_height != -1 or min_width != -1
        self.target_path = _target_path
        # if target folder is empty reset file name back to 0001
        self.reset_counter_on_empty = reset_counter_on_empty
        path = Path(_target_path)

        file_mask = re.compile("^\d*\d{4}$")
        for file in path.iterdir():
            if file_mask.search(file.stem) is None:
                continue
            file_index = int(file.stem)
            if file_index >= self.c:
                self.c = file_index + 1
        

    def on_created(self, event: FileSystemEvent) -> None:
        super().on_created(event)
        self.watcher[event.src_path] = time()
        self.queue.append(event.src_path)
        self.track_file_complete()
    

    def on_modified(self, event: FileSystemEvent) -> None:
        super().on_modified(event)
        if event.src_path in self.watcher:
            self.watcher[event.src_path] = time()
        self.track_file_complete()
    

    def track_file_complete(self, timer = None) -> None:
        if len(self.queue) == 0:
            return
        
        if self.queue_cursor > 1000:
            self.queue = self.queue[self.queue_cursor:]
            self.queue_cursor = 0

        if timer is None:
            timer = time()
        
        cur_file = self.queue[self.queue_cursor]
        # normally should not happen:
        while cur_file not in self.watcher and self.queue_cursor < len(self.queue):
            self.queue_cursor += 1
            cur_file = self.queue[self.queue_cursor]
        
        if cur_file in self.watcher and timer - self.watcher[cur_file] > 5:
            self.handle_file(cur_file)
            del self.watcher[cur_file]
            self.queue_cursor += 1
            if self.queue_cursor == len(self.queue):
                self.queue = []
                self.queue_cursor = 0
            self.track_file_complete(timer)
            return


    def handle_file(self, file_path) -> None:
        if not Path.is_file(Path(file_path)):
            return
        file_desc = from_file(file_path)
        extension = self.file_type_re.findall(file_desc)[-1].lower()
        if extension == "jpeg":
            extension = "jpg"
        if extension == "riff":
            extension = "webp"
        if extension not in self.file_types:
            return
        if self.limit_dimensions and extension in ["png", "jpg", "gif", "webp"]:
            dim = self.image_size_re.findall(file_desc)[-1]
            if self.min_width != -1 and int(dim[0]) < self.min_width:
                return
            if self.min_height != -1 and int(dim[1]) < self.min_height:
                return
        
        if self.reset_counter_on_empty:
            reset = True
            for _ in Path(self.target_path).iterdir():
                reset = False
                break
            if reset:
                self.c = 1

        copy_path = f"{self.target_path}\\{self.c:04}.{extension}"
        self.c += 1
        copy(file_path, copy_path)
