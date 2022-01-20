#!/usr/bin/env python3
"""Checks a directory of Climate Normals files for schema consistency.

This is part of research into the dataset -- do all files have the same schema?

The single argument should be a directory which holds the CSV files. E.g. `scripts/check_schema.py
normals-monthly/2006-2020/access`.
"""

import csv
import os
import sys
import warnings
from collections import defaultdict

import tqdm

if len(sys.argv) != 2:
    print(f"Invalid number of arguments (expected one): {sys.argv}")
    sys.exit(1)

directory = sys.argv[1]

if not os.path.isdir(directory):
    print(f"Path is not a directory: {directory}")
    sys.exit(1)

schema: defaultdict[str, int] = defaultdict(int)
for path in tqdm.tqdm([
        os.path.join(directory, file_name)
        for file_name in os.listdir(directory)
        if os.path.splitext(file_name)[1] == ".csv"
]):
    with open(path) as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if not header:
            warnings.warn(f"File is missing a header row: {path}")
            continue
        for field in header:
            schema[field] += 1

values = list(schema.values())
if all(value == values[0] for value in values):
    print("All schemas are equal!")
    sys.exit(0)
else:
    print("Not all schemas are equal!")
    for key, value in schema.items():
        print(f"{key}: {value}")
    sys.exit(1)
