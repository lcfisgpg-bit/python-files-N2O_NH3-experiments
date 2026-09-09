import pyvisa as visa
import numpy as np

class Standford_SR830:
    def __init__(self, resource_name: str = "GPIB0::8::INSTR") -> None:
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

    def measure(self):
        self.X, self.Y, self.R, self.phase, self.f = map(
            np.float64, self._visa.query("SNAP?1,2,3,4,9").split(",")
        )

    def set_frequency(self, frequency: float) -> None:
        self._visa.write(f"FREQ {frequency}")

    def set_harmonic(self, harmonic: int) -> None:
        measured_harmonic = int(self._visa.query("HARM?"))
        if measured_harmonic != harmonic:
            self._visa.write(f"HARM {harmonic}")


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
        measure_temp(): Measures the current temperature of the laser and updates the temp attribute.

    """

    def __init__(self, resource_name="USB0::0x1313::0x804A::M00884527::INSTR") -> None:
        self.t = None  # temperature

        self._visa = visa.ResourceManager().open_resource(resource_name)

    def set_temp(self, temperature: float) -> None:
        measured_temp = float(self._visa.query("MEAS:TEMP?"))
        if abs(measured_temp - temperature) < 1.1:
            self._visa.write(f"SOUR2:TEMP {temperature}")
        else:
            raise ValueError(
                f"Measured laser temperature ({measured_temp} °C) is not within 1.0 °C of the set laser temperature ({temperature} °C)."
            )

    def measure_temp(self) -> float:
        self.t = float(self._visa.query("MEAS:TEMP?"))
        return self.t

    def set_ext_modulation(self, enable: bool) -> None:
        """
        Enable or disable external modulation for the laser.

        Parameters:
            enable (bool): True to enable external modulation, False to disable.
        """
        if enable:
            self._visa.write("SOUR:AM:SOURce EXTernal")
        else:
            self._visa.write("SOUR:AM:SOURce INTernal")

    def set_laser_current(self, current: float) -> None:
        """
        Set the laser current.

        Parameters:
            current (float): The desired laser current in Amperes.
        """
        measured_current = float(self._visa.query(f"MEAS:CURR?"))
        if abs(measured_current - current) < 0.011:
            self._visa.write(f"SOUR:CURR {current}")
        else:
            raise ValueError(
                f"Measured laser current ({measured_current} A) is not within 0.010 A of the set laser current ({current} A)."
            )


class Rigol_DG832:
    def __init__(
        self,
        resource_name="USB0::0x1AB1::0x643::DG8A244803802::INSTR",
        waveform="SINusoid",
        amplitude=1e-3,
        offset=0.0,
        frequency=1e3,
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

    def check_channel(func):
        def inner(*args, **kwargs):
            channel = kwargs.get("channel", 1)
            if channel not in [1, 2]:
                raise ValueError("Channel must be 1 or 2.")
            result = func(*args, **kwargs)
            return result
        return inner

    @check_channel
    def set_offset(self, voltage: float = 0.0, channel: int = 1) -> None:
        self.offset = voltage
        self._visa.write(f":SOURce{channel}:VOLTage:OFFSet {self.offset}")

    @check_channel
    def set_amplitude(self, voltage: float = 0.0, channel: int = 1) -> None:
        measured_amplitude = float(self._visa.query(f":SOURce{channel}:VOLTage:AMPLitude?"))
        if abs(measured_amplitude - voltage) < 0.151:
            self.amplitude = voltage
            self._visa.write(f":SOURce{channel}:VOLTage:AMPLitude {self.amplitude}")
        else:
            raise ValueError(
                f"Measured amplitude ({measured_amplitude} V) is not within 150 mV of the desired amplitude ({voltage} V)."
            )

    @check_channel
    def set_waveform(self, waveform: str, channel: int = 1) -> None:
        if waveform not in ["SINusoid", "SQUare", "RAMP"]:
            raise ValueError("Waveform must be one of 'SINusoid', 'SQUare', or 'RAMP'.")
        self.waveform = waveform
        self._visa.write(f":SOURce{channel}:APPL:{waveform}")

    @check_channel
    def set_frequency(self, frequency: float, channel: int = 1) -> None:
        self.frequency = frequency
        self._visa.write(f":SOURce{channel}:FREQuency {frequency}")

    @check_channel
    def set_phase(self, phase: float, channel: int = 1) -> None:
        self._visa.write(f":SOURce{channel}:PHASe:COUPle:OFFSet {phase}")

    @check_channel
    def on(self, channel: int = 1) -> None:
        self._visa.write(f":OUTPut{channel}:STATe ON")

    @check_channel
    def off(self, channel: int = 1) -> None:
        self._visa.write(f":OUTPut{channel}:STATe OFF")
