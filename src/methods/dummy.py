from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'dummy'

    def initialize(self):
        pass

    def calculate_charges(self, molecule):
        return [0.0 for _ in molecule]
