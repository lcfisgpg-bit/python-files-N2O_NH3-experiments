import pyvisa as visa
import numpy as np


class Standford_SR830:
    def __init__(self, resource_name="GPIB0::8::INSTR") -> None:
        self.X = None  # in-phase component
        self.Y = None  # quadrature component
        self.R = None  # magnitude
        self.phase = None  # phase
        self.f = None  # frequency

        self._visa = visa.ResourceManager().open_resource(resource_name)
        self._visa.timeout = 5000  # Increase the timeout to 5 seconds
        self._visa.write_termination = "\n"
        self._visa.read_termination = "\n"
        self._visa.clear()  # Clear the buffer of SR830

    def read(self):
        self.X, self.Y, self.R, self.phase, self.f = map(
            np.float64, self._visa.query("SNAP?1,2,3,4,9").split(",")
        )

    def write_frequency(self, frequency):
        self._visa.write(f"FREQ {frequency}")


class Thorlabs_ITC4002QCL:
    """
    Class to control the laser temperature source.

    Parameters:
        resource_name (str): The VISA resource name for the laser temperature source.
            Default:     'USB0::0x1313::0x804A::M00884527::INSTR' for NH3 laser.
            Alternative: 'USB0::0x1313::0x804A::M00977996::INSTR' for N2O laser.

    Attributes:
        temp (float): The current temperature of the laser.
        _visa (pyvisa.resources.Resource): The VISA resource for communication with the laser.

    Methods:
        set_temp(temperature): Sets the temperature of the laser to the specified value.
        read_temp(): Reads the current temperature of the laser and updates the temp attribute.

    """

    def __init__(self, resource_name="USB0::0x1313::0x804A::M00884527::INSTR") -> None:
        self.t = None  # temperature

        self._visa = visa.ResourceManager().open_resource(resource_name)

    def set_temp(self, temperature):
        self._visa.write(f"SOUR2:TEMP {temperature}")

    def read_temp(self) -> float:
        self.t = float(self._visa.query("MEAS:TEMP?"))
        return self.t


class Rigol_DG832:
    def __init__(
        self,
        resource_name="USB0::0x1AB1::0x643::DG8A244803802::INSTR",
        waveform="SINusoid",
        amplitude=1.0,
        offset=0.0,
        frequency=1000.0,
    ) -> None:
        self.waveform = waveform
        self.amplitude = amplitude
        self.offset = offset
        self.frequency = frequency

        self._visa = visa.ResourceManager().open_resource(resource_name)
        self._visa.timeout = 5000  # Increase the timeout to 5 seconds
        self._visa.write_termination = "\n"
        self._visa.read_termination = "\n"
        self._visa.clear()  # Clear the buffer of DG832

    def set_offset(self, voltage=0.0, channel=1):
        self.offset = voltage
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self._visa.write(f":SOURce{channel}:VOLTage:OFFSet {self.offset}")

    def set_amplitude(self, voltage=0.0, channel=1):
        self.amplitude = voltage
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self._visa.write(f":SOURce{channel}:VOLTage:AMPLitude {self.amplitude}")

    def set_waveform(self, waveform, channel=1):
        if waveform not in [
            "SINusoid",
            "SQUare",
            "TRIangle",
            "RAMP",
            "NRAMp",
            "NOISe",
            "ARB",
        ]:
            raise ValueError(
                "Waveform must be one of 'SINusoid', 'SQUare', 'TRIangle', 'RAMP', 'NRAMp', 'NOISe', or 'ARB'."
            )
        self.waveform = waveform
        # self._visa.write(f':SOURce{channel}:AM:INTernal:FUNCtion {waveform}')
        # self._visa.write(f':SOURce{channel}:FUNCtion:{waveform}')
        self._visa.write(f":SOURce{channel}:APPL:{waveform}")

    def set_frequency(self, frequency, channel=1):
        self.frequency = frequency
        self._visa.write(f":SOURce{channel}:FREQuency {frequency}")

    def set_phase(self, phase, channel=1):
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2.")
        self._visa.write(f":SOURce{channel}:PHASe:COUPle:OFFSet {phase}")
