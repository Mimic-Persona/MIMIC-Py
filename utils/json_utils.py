import json
import os
from typing import Any
import random


def read_json(
        path: str
) -> Any:
    """
    Reads a JSON file and returns the data as a Python object (dictionary or list).
    :param path: The file path to the JSON file.
    :return: A Python object (dictionary or list) parsed from the JSON file.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(
        obj: Any,
        path: str,
        indent: int = 2
):
    """
    Writes data to a JSON file.
    :param obj: The obj to write, can be a dictionary or a list.
    :param path: The file path where the JSON data will be written.
    :param indent: The number of spaces to use for indentation in the JSON file. Default is 2.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)


def append_json(
        obj: Any,
        path: str
):
    """
    Appends an object to a JSON file. If the file does not exist, it creates a new one.
    :param obj: The object to append, can be a dictionary or a list.
    :param path: The file path where the JSON data will be appended.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(path))
    try:
        data = read_json(path)
        if isinstance(data, list):
            data.append(obj)
        else:
            data = [data, obj]
    except FileNotFoundError:
        data = [obj]
    write_json(data, path)


def read_jsonl(
        path: str
) -> list[Any]:
    """
    Reads a JSON Lines (JSONL) file and returns a list of JSON objects.
    :param path: The file path to the JSONL file.
    :return: A list of JSON objects read from the file.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(
        records: list[Any],
        path: str
):
    """
    Writes a list of records to a JSON Lines (JSONL) file.
    :param records: A list of JSON objects to write to the file.
    :param path: The file path where the JSONL data will be written.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def append_jsonl(
        record: Any,
        path: str
):
    """
    Appends a single JSON object to a JSON Lines (JSONL) file.
    :param record: The JSON object to append to the file.
    :param path: The file path where the JSONL data will be appended.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(path))
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


def json_to_str(
        obj: Any,
        indent: int = 2
) -> str:
    """
    Converts a Python object to a JSON string with specified indentation.
    :param obj: The Python object to convert to JSON string.
    :param indent: The number of spaces to use for indentation in the JSON string. Default is 2.
    :return: A JSON string representation of the object.
    """
    return json.dumps(obj, indent=indent, ensure_ascii=False)


def str_to_json(
        json_str: str
) -> Any:
    """
    Converts a JSON string to a Python object.
    :param json_str: The JSON string to convert.
    :return: A Python object (dictionary or list) parsed from the JSON string.
    """
    return json.loads(json_str)


def str_to_jsonl_lines(
        jsonl_str: str
) -> list[Any]:
    """
    Converts a JSON Lines (JSONL) string to a list of JSON objects.
    :param jsonl_str: The JSON Lines string to convert.
    :return: A list of JSON objects parsed from the JSON Lines string.
    """
    return [json.loads(line) for line in jsonl_str.splitlines() if line.strip()]


def jsonl_lines_to_str(
        records: list[Any]
) -> str:
    """
    Converts a list of JSON objects to a JSON Lines (JSONL) string.
    :param records: A list of JSON objects to convert to a JSON Lines string.
    :return: A JSON Lines string representation of the list of records.
    """
    return '\n'.join(json.dumps(record, ensure_ascii=False) for record in records)


def file_exists(file_path: str) -> bool:
    """
    Checks if a file exists at the given path.
    :param file_path: The path to the file to check.
    :return: True if the file exists, False otherwise.
    """
    return os.path.isfile(file_path)


def ensure_dir_exists(path: str):
    """
    Ensures that the directory at the given path exists, creating it if necessary.
    :param path: The path to the directory to ensure it exists.
    :return: None
    """
    os.makedirs(path, exist_ok=True)

def json_to_jsonl(
        input_path: str,
        output_path: str
):
    """
    Converts a JSON file to a JSON Lines (JSONL) file.
    :param input_path: The file path to the input JSON file.
    :param output_path: The file path where the output JSONL data will be written.
    :return: None
    """
    data = read_json(input_path)
    if isinstance(data, list):
        write_jsonl(data, output_path)
    else:
        write_jsonl([data], output_path)


def split_jsonl_to_train_val_test(
        input_path: str,
        train_path: str,
        val_path: str,
        test_path: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 111
):
    """
    Splits a JSON Lines (JSONL) file into training, validation, and test sets.
    :param input_path: The file path to the input JSONL file.
    :param train_path: The file path where the training set will be written.
    :param val_path: The file path where the validation set will be written.
    :param test_path: The file path where the test set will be written.
    :param train_ratio: The ratio of the data to use for the training set. Default is 0.8.
    :param val_ratio: The ratio of the data to use for the validation set. Default is 0.1.
    :param test_ratio: The ratio of the data to use for the test set. Default is 0.1.
    :param seed: The random seed for shuffling the data before splitting. Default is 111.
    :return: None
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1."

    records = read_jsonl(input_path)

    # Shuffle records for randomness with a fixed seed
    random.seed(seed)
    random.shuffle(records)

    total = len(records)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    train_records = records[:train_end]
    val_records = records[train_end:val_end]
    test_records = records[val_end:]

    print(f"Total records: {total}")
    print(f"Training records: {len(train_records)}")
    print(f"Validation records: {len(val_records)}")
    print(f"Test records: {len(test_records)}")

    write_jsonl(train_records, train_path)
    write_jsonl(val_records, val_path)
    write_jsonl(test_records, test_path)