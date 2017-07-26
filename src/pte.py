import csv
from collections import namedtuple
from typing import Dict

Element = namedtuple('Element', 'number symbol name mass electronegativity'.split())

PTE_CSV_FILE = '../data/pte.csv'


def load_pte_from_file(filename: str) -> Dict:
    pte = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for item in reader:
            types = (int, str, str, float, float)
            properties = ('Atomic Number', 'Symbol', 'Element', 'Atomic Weight', 'Electronegativity')
            try:
                data = (prop_type(item[prop]) for prop_type, prop in zip(types, properties))
                element = Element(*data)
            except ValueError:
                print('Something\'s wrong with the PTE element {}'.format(item['Symbol']))
                continue

            pte[element.symbol] = element
    return pte


periodic_table = load_pte_from_file(PTE_CSV_FILE)
