__all__ = ["ProxrSerial"]

import asyncio
import time
import proxr_protocol as pp
from typing import Dict, Any, List


from yaqd_core import aserial
from yaqd_core import IsDaemon, HasPosition, IsDiscrete, UsesSerial, UsesUart


class ProxrSerial(IsDiscrete, HasPosition, UsesUart, UsesSerial, IsDaemon):
    _kind = "proxr-serial"
    _serial_objects: Dict[str, aserial.ASerial] = dict()

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        if self._config["serial_port"] in ProxrSerial._serial_objects:
            self._serial = ProxrSerial._serial_objects[self._config["serial_port"]]
        else:
            self._serial = aserial.ASerial()
            self._serial.port = self._config["serial_port"]
            self._serial.baudrate = self._config["baud_rate"]
            self._serial.eol = b"\r"
            self._serial.open()
            ProxrSerial._serial_objects[self._config["serial_port"]] = self._serial

    def close(self):
        self._serial.close()

    def direct_serial_write(self, message):
        self._serial.write(message)

    def _set_position(self, position):
        if position == 0:
            self._serial.write(pp.relay_off_by_bank(self._config["relay"], self._config["bank"]))
        elif position == 1:
            self._serial.write(pp.relay_on_by_bank(self._config["relay"], self._config["bank"]))
        else:
            raise NotImplementedError()  # error handling for bad position
        time.sleep(0.5)  # ProXR board requires some processing time

    async def update_state(self):
        """Continually monitor and update the current daemon state."""
        # If there is no state to monitor continuously, delete this function
        while True:
            # Perform any updates to internal state
            self._busy = False
            # There must be at least one `await` in this loop
            # This one waits for something to trigger the "busy" state
            # (Setting `self._busy = True)
            # Otherwise, you can simply `await asyncio.sleep(0.01)`
            await asyncio.sleep(0.01)
