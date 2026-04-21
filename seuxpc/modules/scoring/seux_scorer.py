from seuxpc.config.settings import ALPHA

class SEUXScorer:

    def compute(self, ux, ux_c, ivs):

        ich = ux / 5
        iac = ux_c / 20

        return {
            "ICH": ich,
            "IAC": iac,
            "IVS": ivs,
            "Brecha": iac - ich
        }