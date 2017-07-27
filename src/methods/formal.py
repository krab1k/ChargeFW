from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'formal'

    def initialize(self):
        pass

    def calculate_charges(self, molecule):
        return [float(atom.formal_charge) for atom in molecule]
