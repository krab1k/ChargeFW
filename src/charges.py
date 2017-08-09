import json
import sys
from typing import Dict

import numpy as np


class Charges:
    def __init__(self, data: Dict[str, np.ndarray]=None) -> None:
        if data is None:
            self._data = {}
        else:
            self._data: Dict[str, np.ndarray] = data

    def __getitem__(self, item: str):
        return self._data[item]

    def __setitem__(self, key: str, value: np.ndarray):
        self._data[key] = value

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data.keys())

    @classmethod
    def load_from_file(cls, filename: str):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except IOError:
            print('Cannot load charges from file: {}'.format(filename), file=sys.stderr)
            sys.exit(1)

        for key, value in data.items():
            data[key] = np.array(value, dtype=np.float32)

        return Charges(data)

    def save_to_file(self, filename: str):
        data_copy = {}
        for key, value in self._data.items():
            data_copy[key] = value.tolist()

        try:
            with open(filename, 'w') as f:
                json.dump(data_copy, f)
        except IOError:
            print('Cannot store charges to file: {}'.format(filename), file=sys.stderr)
            sys.exit(1)
