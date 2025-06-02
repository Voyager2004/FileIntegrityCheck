# -*- coding: utf-8 -*-
# record_manager.py

import json
import os

RECORD_FILE = 'hash_record.json'


def load_record() -> dict:
    """
    Load the JSON file and return in the following format:
    {
      "file_path_1": {"hash": "...", "remark": "..."},
      "file_path_2": {"hash": "...", "remark": "..."}
    }

    """
    if not os.path.exists(RECORD_FILE):
        return {}
    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except:
            return {}


def save_record(record: dict):
    """
    Write the records back to the JSON file.
    """
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=4)


def add_file_hash(file_path: str, hash_value: str, remark: str = None):
    """
    Add/update the file's hash record.
    If the remark is an empty string or None, retain the original remark (if it already exists).

    """
    record = load_record()
    if file_path in record:
        # If the record for the file already exists, only update the hash and the remark (if the remark is not empty).
        old_remark = record[file_path].get("remark", "")
        record[file_path]["hash"] = hash_value
        # If the remark passed in this time is not None, update it. Otherwise, retain the old one.
        if remark is not None:
            record[file_path]["remark"] = remark
        else:
            record[file_path]["remark"] = old_remark
    else:
        # If it does not exist, create a new one.
        record[file_path] = {"hash": hash_value, "remark": remark if remark else ""}
    save_record(record)


def get_file_hash(file_path: str):
    """
    Return the file's hash value (as a string); return None if it does not exist.
    """
    record = load_record()
    info = record.get(file_path, None)
    if info:
        return info.get("hash", None)
    return None


def get_file_remark(file_path: str) -> str:
    """
    Get the remark name; return an empty string if none exists.
    """
    record = load_record()
    info = record.get(file_path, None)
    if info:
        return info.get("remark", "")
    return ""


def update_file_remark(file_path: str, new_remark: str):
    """
    Update the file's remark name.
    """
    record = load_record()
    if file_path in record:
        record[file_path]["remark"] = new_remark
        save_record(record)


def get_all_records() -> dict:
    """
    Return all current records：
    {
      "file_path_1": {"hash": "...", "remark": "..."},
      "file_path_2": {"hash": "...", "remark": "..."}
    }
    """
    return load_record()
