import numpy as np

from pte import Element


class Atom:
    __slots__ = ['_element', '_index', '_coordinates', '_formal_charge', '_atom_type']

    def __init__(self, element: Element, index: int, coordinates: np.ndarray, charge: int) -> None:
        self._element: Element = element
        self._index: int = index
        self._coordinates: np.array = np.array(coordinates, dtype=np.float32)
        self._formal_charge: int = charge
        self._atom_type = None

    def __repr__(self):
        name = type(self).__name__
        return "{}('{}', {})".format(name, self.element, self.coordinates)

    def __str__(self):
        return 'Atom({}, idx={}, chg={})'.format(self.element.symbol, self.index, self.formal_charge)

    @property
    def element(self):
        return self._element

    @property
    def index(self):
        return self._index

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def formal_charge(self):
        return self._formal_charge

    @property
    def atom_type(self):
        return self._atom_type

    @atom_type.setter
    def atom_type(self, value):
        self._atom_type = value
