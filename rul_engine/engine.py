"""High-level engine orchestrating TPMS RUL computation and diagnostics."""

from . import calibration, leak_detection, pressure_rul, tread_rul, confidence


class TPMSPipe:
    def __init__(self):
        pass

    def run(self, data):
        """Process incoming data and return RUL and alerts."""
        pass
