from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'formal'
    FULL_NAME = 'Formal charges'

    def initialize(self, options):
        pass

    def calculate_charges(self, molecule):
        return [float(atom.formal_charge) for atom in molecule]
