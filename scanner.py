import os
import json
import time
from typing import Callable
from threading import Thread


def count_directories(tree):
    count = 1
    for subdir in tree[2]:
        count += count_directories(subdir)
    return count


class Scanner:
    def __init__(self):
        self.scanned_files = 0
        self.scanned_directories = 0
        self.scanned_memory_in_bytes = 0
        self.scan_result = None
        self.scan_thread = None
        self.force_scan_stop = False
        self.on_scan_finished_callback = lambda: None
        self.update_callback = lambda files, directories, bytes: None
        self.can_modify_ui = False

    def start_scan(self, dir_path: str) -> bool:
        if self.scan_thread is not None and self.scan_thread.is_alive():
            return False

        self.can_modify_ui = True
        self.clear_scan_stats()

        self.scan_result = None
        self.force_scan_stop = False

        self.scan_thread = Thread(target=self.scan_dir, args=(dir_path, 0))
        self.scan_thread.start()

        return True

    def end_scan(self):
        if self.scan_thread is None:
            return

        if self.scan_thread.is_alive():
            self.can_modify_ui = False
            self.force_scan_stop = True
            self.scan_thread.join()

    def clear_scan_stats(self):
        self.scanned_files = 0
        self.scanned_directories = 0
        self.scanned_memory_in_bytes = 0

    def scan_dir(self, dir_path: str, depth: int = 0):
        if self.force_scan_stop:
            return [dir_path, 0, []]

        dir_size = 0
        dir_children = []

        for element_name in os.listdir(dir_path):
            element_real_path = os.path.join(dir_path, element_name)

            if os.path.isfile(element_real_path):
                file_size = os.path.getsize(element_real_path)
                self.scanned_files += 1
                self.scanned_memory_in_bytes += file_size
                dir_size += file_size

            if os.path.isdir(element_real_path):
                try:
                    branch = self.scan_dir(element_real_path, depth + 1)
                    self.scanned_directories += 1
                    dir_size += branch[1]
                    dir_children.append(branch)
                except PermissionError:
                    continue

        if self.can_modify_ui:
            self.update_callback(self.scanned_files, self.scanned_directories, self.scanned_memory_in_bytes)

        if depth == 0:
            self.scan_result = [dir_path, dir_size, dir_children]
            self.on_scan_finished_callback()
        else:
            return [dir_path, dir_size, dir_children]

    @property
    def is_scanning(self):
        return self.scan_thread.is_alive() if self.scan_thread is not None else False

    def load_scan_data(self, path: str):
        self.clear_scan_stats()
        with open(path, "r") as json_file:
            self.end_scan()
            self.scan_result = json.load(json_file)
            self.scanned_directories = count_directories(self.scan_result)
            self.scanned_memory_in_bytes = self.scan_result[1]
            self.scanned_files = -1
            self.update_callback(self.scanned_files, self.scanned_directories, self.scanned_memory_in_bytes)

    def save_scan_data(self, path: str):
        if self.scan_result is None:
            return

        if os.path.dirname(path):
            with open(path, "w") as scan_result_file:
                json.dump(self.scan_result, scan_result_file)

    def bind_on_scanned_finished(self, callback: Callable[[], None]):
        self.on_scan_finished_callback = callback

    def bind_label_update_callback(self, callback: Callable[[int, int, int], None]):
        self.update_callback = callback


def format_bytes(bytes: int) -> str:
    suffixes = ["b", "kb", "mb", "gb", "tb", "pb"]
    suffix = 0

    if bytes < 1024:
        return f"{bytes}b"

    while bytes >= 1024:
        bytes *= 0.0009765625
        suffix += 1

    return f"{bytes: .2f}{suffixes[suffix]}"


def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    scanner = Scanner()
    scanner.start_scan(current_dir)

    while scanner.is_scanning:
        print("Scan is in progress... doing other work.")
        time.sleep(1)

    print(scanner.scan_result)


if __name__ == "__main__":
    main()
