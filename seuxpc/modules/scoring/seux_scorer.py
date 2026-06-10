from seuxpc.config.settings import SCORING_VERSION


class SEUXScorer:

    def compute(self, ux, ux_c, ivs, ux_norm=None, ux_c_norm=None):

        ich = ux / 5
        iac = ux_c / 20

        # Nueva escala estandarizada 0-1 para comparabilidad entre indices.
        # Se mantiene ICH/IAC legacy para compatibilidad historica.
        if ux_norm is None:
            ich_norm = ich
        else:
            ich_norm = max(0.0, min(1.0, float(ux_norm)))

        if ux_c_norm is None:
            iac_norm = max(0.0, min(1.0, iac))
        else:
            iac_norm = max(0.0, min(1.0, float(ux_c_norm)))

        brecha_norm_signed = iac_norm - ich_norm
        brecha_norm = (brecha_norm_signed + 1.0) / 2.0

        return {
            "scoring_version": SCORING_VERSION,
            "ICH": ich,
            "IAC": iac,
            "IVS": ivs,
            "Brecha": iac - ich,
            "ICH_norm": ich_norm,
            "IAC_norm": iac_norm,
            "Brecha_norm_signed": brecha_norm_signed,
            "Brecha_norm": brecha_norm,
        }