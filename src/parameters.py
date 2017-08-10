import json
import sys
from collections import OrderedDict
from typing import List, Tuple, Dict

import numpy as np


class ParameterError(Exception):
    pass


class AtomParameterMeta:
    @classmethod
    def create_type(cls, parameter_names):
        def __init__(self, *args):
            self.__dict__ = OrderedDict.fromkeys(parameter_names)
            if len(self.__dict__) != len(args):
                raise ParameterError('Invalid number of arguments')
            for attr, value in zip(self.__dict__.keys(), args):
                self.__dict__[attr] = float(value)

        def __repr__(self):
            return 'AtomParameter({args})'.format(args=', '.join('{:.3f}'.format(v) for v in self.__dict__.values()))

        d = {'parameter_names': parameter_names, '__init__': __init__, '__repr__': __repr__}
        return type('AtomParameter', (), d)


class Parameters:
    def __init__(self, common_parameters: List[str], atom_parameters: List[str]):
        try:
            self._common = CommonParameters(common_parameters)
            self._atom = AtomParameters(atom_parameters)
        except ValueError:
            raise ParameterError('Duplicate parameter names')

        self._common_ranges: Dict[str, Tuple[float, float]] = None
        self._atom_ranges: Dict[str, Tuple[float, float]] = None

    @property
    def common(self):
        return self._common

    @property
    def atom(self):
        return self._atom

    @property
    def size(self):
        return len(self.common) + len(self.atom) * len(self.atom.parameter_names)

    def load_from_file(self, filename: str):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except IOError:
            print('Cannot load parameters from file: {}'.format(filename), file=sys.stderr)
            sys.exit(1)

        for parameter in data['common']:
            if parameter not in self.common.parameter_names:
                raise ParameterError('Parameter with name {} not defined'.format(parameter))
            self.common[parameter] = float(data['common'][parameter])

        for parameter in data['atom']:
            self.atom.add_parameter(parameter[0], parameter[1], parameter[2], parameter[3:])

    def init_from_set(self, molecules):
        for name in self.common.parameter_names:
            self.common[name] = 0.0

        for element, classifier, atom_type in molecules.atom_types:
            self.atom.add_parameter(element, classifier, atom_type, [0.0] * len(self.atom.parameter_names))

    def set_random_values(self):
        if self._atom_ranges is None or self._common_ranges is None:
            self.load_packed(np.random.rand(self.size))
        else:
            for parameter in self.common:
                self.common[parameter] = np.random.uniform(*self._common_ranges[parameter])

            packed = np.empty(len(self.atom) * len(self.atom.parameter_names), dtype=np.float_)
            for i, parameter_name in enumerate(self.atom.parameter_names):
                low, high = self._atom_ranges[parameter_name]
                packed[i::len(self.atom.parameter_names)] = np.random.uniform(low, high, len(self.atom))

            self.atom.update_values(packed)

    def set_ranges(self, common_ranges: Dict[str, Tuple[float, float]], atom_ranges: Dict[str, Tuple[float, float]]):
        assert common_ranges.keys() == set(self.common.parameter_names)
        assert atom_ranges.keys() == set(self.atom.parameter_names)
        self._common_ranges = common_ranges
        self._atom_ranges = atom_ranges

    def pack_values(self) -> np.ndarray:
        packed = np.empty(self.size, dtype=np.float_)
        idx = 0
        for parameter in self.common:
            packed[idx] = self.common[parameter]
            idx += 1

        for parameter in self.atom:
            for value in parameter[3:]:
                packed[idx] = value
                idx += 1

        return packed

    def load_packed(self, packed: np.ndarray):
        assert len(packed) == self.size

        start = 0
        for i, key in enumerate(self.common):
            self.common[key] = packed[i]
            start = i

        self.atom.update_values(packed[start:])

    def print_parameters(self):
        print('Common parameters:')
        for parameter in self.common:
            print('{}: {:.3}'.format(parameter, self.common[parameter]))

        print('Atom parameters:')
        for parameter in self.atom:
            print('{}: {}'.format(parameter, self.atom.parameter_values(parameter)))


class CommonParameters:
    def __init__(self, parameter_names):
        self._parameter_names = parameter_names
        self._parameters = OrderedDict()

    def __iter__(self):
        return iter(self._parameters)

    def __getitem__(self, item):
        try:
            return self._parameters[item]
        except KeyError:
            raise ParameterError('No parameter named {}'.format(item))

    def __setitem__(self, key, value):
        if key not in self._parameter_names:
            raise ParameterError('No parameter {} defined'.format(key))

        self._parameters[key] = value

    def __len__(self):
        return len(self._parameters)

    @property
    def parameter_names(self):
        return self._parameter_names


class AtomParameters:
    def __init__(self, parameter_names):
        self._type = AtomParameterMeta.create_type(parameter_names)
        self._parameters: OrderedDict[Tuple[str, str, str]] = OrderedDict()

    def __iter__(self):
        return iter(self._parameters)

    def __len__(self):
        return len(self._parameters)

    def __getitem__(self, item):
        def f(atom):
            try:
                return self._parameters[atom.atom_type].__dict__[item]
            except AttributeError:
                raise ParameterError('No parameter {} defined'.format(item))
            except KeyError:
                raise ParameterError('No suitable parameter found for {}'.format(atom))

        return f

    def add_parameter(self, element: str, classifier: str, atom_type: str, parameters):
        if parameters in self:
            raise ParameterError('Parameter already defined')

        self._parameters[(element, classifier, atom_type)] = self._type(*parameters)

    def update_values(self, values: np.ndarray):
        values_count = len(self.parameter_names)
        for i, key in enumerate(self._parameters):
            self._parameters[key] = self._type(*values[i * values_count: (i + 1) * values_count])

    def parameter_values(self, parameter: Tuple[str, str, str]):
        return self._parameters[parameter]

    @property
    def parameter_names(self):
        # noinspection PyUnresolvedReferences
        return self._type.parameter_names
