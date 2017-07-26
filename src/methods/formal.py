from charge_method import ChargeMethod


class FormalChargeMethod(ChargeMethod):
    def initialize(self):
        pass

    def calculate_charges(self, molecule):
        return [float(atom.formal_charge) for atom in molecule]
