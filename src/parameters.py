import json
import sys
from collections import namedtuple, OrderedDict
from typing import List

import numpy as np

from classifier import classifiers


class ParameterError(Exception):
    pass


class Parameters:
    def __init__(self, common_parameters: List[str], atom_parameters: List[str]):
        try:
            self._common = CommonParameters(namedtuple('CommonParamater', 'name value'), common_parameters)
            self._atom = AtomParameters(
                namedtuple('AtomParameter', 'element classifier atom_type ' + ' '.join(atom_parameters)),
                atom_parameters)
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
            self.atom.add_parameter(self.atom.type(*parameter))

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
            start += 1

        values_count = len(self.atom.parameter_names)
        for i, p in enumerate(self.atom):
            values = packed[start + i * values_count: start + (i + 1) * values_count]
            self.atom.update_values(i, values)


class CommonParameters:
    def __init__(self, parameter_type, parameter_names):
        self._type = parameter_type
        self._parameter_names = parameter_names
        self._parameters = OrderedDict()
        self.items = self._parameters.items

    def __iter__(self):
        return iter(self._parameters.keys())

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
    def __init__(self, parameter_type, parameter_names):
        self._type: namedtuple = parameter_type
        self._parameter_names: List[str] = parameter_names
        self._parameters: List[parameter_type] = []

    def __iter__(self):
        return iter(self._parameters)

    def __len__(self):
        return len(self._parameters)

    def add_parameter(self, parameter):
        if parameter in self:
            raise ParameterError('Parameter already defined')

        self._parameters.append(parameter)

    def update_values(self, parameter_idx, values):
        header = self._parameters[parameter_idx][:3]
        self._parameters[parameter_idx] = self.type(*header, *values)

    def __getitem__(self, item):
        def f(molecule, atom):
            for parameter in self._parameters:
                if self.matches(parameter, molecule, atom):
                    try:
                        return getattr(parameter, item)
                    except AttributeError:
                        raise ParameterError('No parameter {} defined'.format(item))
            else:
                raise ParameterError('No suitable parameter found for {}'.format(atom))

        return f

    @staticmethod
    def matches(parameter, molecule, atom):
        if parameter.element != atom.element.symbol:
            return False
        try:
            classifier = classifiers[parameter.classifier]
        except KeyError:
            raise ParameterError('No such classifier: {}'.format(parameter.classifier))

        return classifier.check(molecule, atom, parameter.atom_type)

    @property
    def type(self):
        return self._type

    @property
    def parameter_names(self):
        return self._parameter_names
