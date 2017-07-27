from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'dummy'
    FULL_NAME = 'Dummy method, outputs zeros'

    def initialize(self, options):
        pass

    def calculate_charges(self, molecule):
        return [0.0 for _ in molecule]
