import abc

from structures.atom import Atom
from structures.molecule import Molecule

classifiers = {}


def atom_classifier(c):
    classifiers[c.string] = c
    return c


class Classifier(abc.ABC):
    string: str = '<empty>'

    @classmethod
    @abc.abstractmethod
    def get_type(cls, molecule: Molecule, atom: Atom):
        pass

    @classmethod
    def check(cls, molecule: Molecule, atom: Atom, atom_type):
        return cls.get_type(molecule, atom) == atom_type


@atom_classifier
class Plain(Classifier):
    string: str = 'plain'

    @classmethod
    def get_type(cls, molecule: Molecule, atom: Atom) -> str:
        return '*'


@atom_classifier
class HBO(Classifier):
    string: str = 'hbo'

    @classmethod
    def get_type(cls, molecule: Molecule, atom: Atom) -> int:
        return molecule.highest_bond_order(atom)
