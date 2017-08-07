import json
import sys
from collections import namedtuple, OrderedDict
from typing import List

import numpy as np


class ParameterError(Exception):
    pass


class Parameters:
    def __init__(self, common_parameters: List[str], atom_parameters: List[str]):
        try:
            self._common = CommonParameters(common_parameters)
            self._atom = AtomParameters(atom_parameters)
        except ValueError:
            raise ParameterError('Duplicate parameter names')

    @property
    def common(self):
        return self._common

    @property
    def atom(self):
        return self._atom

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

    def pack_values(self) -> np.ndarray:
        size = len(self.common) + len(self.atom) * len(self.atom.parameter_names)
        packed = np.empty(size, dtype=np.float32)
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
        assert len(packed) == len(self.common) + len(self.atom) * len(self.atom.parameter_names)

        start = 0
        for i, key in enumerate(self.common):
            self.common[key] = packed[i]
            start = i

        self.atom.update_values(packed[start:])

    def print_parameters(self):
        print('Common parameters:')
        for parameter in self.common:
            print('{}: {}'.format(parameter, self.common[parameter]))

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
        self._type: namedtuple = namedtuple('AtomParameter', ' '.join(parameter_names))
        self._parameters: OrderedDict[tuple, tuple] = OrderedDict()

    def __iter__(self):
        return iter(self._parameters)

    def __len__(self):
        return len(self._parameters)

    def __getitem__(self, item):
        def f(atom):
            try:
                return getattr(self._parameters[atom.atom_type], item)
            except AttributeError:
                raise ParameterError('No parameter {} defined'.format(item))
            except KeyError:
                raise ParameterError('No suitable parameter found for {}'.format(atom))

        return f

    def add_parameter(self, element: str, classifier: str, atom_type: str, parameters):
        if parameters in self:
            raise ParameterError('Parameter already defined')

        self._parameters[(element, classifier, atom_type)] = self._type(*parameters)

    def update_values(self, values):
        values_count = len(self.parameter_names)
        for i, key in enumerate(self._parameters):
            self._parameters[key] = self._type(*values[i * values_count: (i + 1) * values_count])

    def parameter_values(self, parameter):
        return self._parameters[parameter]

    @property
    def parameter_names(self):
        # noinspection PyProtectedMember
        return self._type._fields
