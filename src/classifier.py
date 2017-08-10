import abc
from typing import Dict, Tuple

from parameters import ParameterError, AtomParameters
from structures.atom import Atom
from structures.molecule import Molecule


class Classifier(abc.ABC):
    string: str = '<empty>'

    @classmethod
    @abc.abstractmethod
    def get_type(cls, molecule: Molecule, atom: Atom):
        pass


classifiers: Dict[str, Classifier] = {}


def atom_classifier(c: Classifier):
    classifiers[c.string] = c
    return c


@atom_classifier
class Plain(Classifier):
    string: str = 'plain'

    @classmethod
    def get_type(cls, molecule: Molecule, atom: Atom) -> Tuple[str, str]:
        return cls.string, '*'


@atom_classifier
class HBO(Classifier):
    string: str = 'hbo'

    @classmethod
    def get_type(cls, molecule: Molecule, atom: Atom) -> Tuple[str, int]:
        return cls.string, molecule.highest_bond_order(atom)


class ParametersClassifier(Classifier):
    string: str = 'parameters'

    def __init__(self, parameters: AtomParameters):
        self._parameters = parameters

    def get_type(self, molecule: Molecule, atom: Atom):
        for classifier, atom_type in self._parameters.data[atom.element.symbol]:
            if classifiers[classifier].get_type(molecule, atom)[1] == atom_type:
                return classifier, atom_type

        raise ParameterError('No parameter found for atom {}'.format(atom.element.symbol))
