from charge_method import ChargeMethod


class DummyChargeMethod(ChargeMethod):
    def initialize(self):
        pass

    def calculate_charges(self, molecule):
        return [0.0 for _ in molecule]
