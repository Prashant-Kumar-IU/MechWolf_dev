from .component import ActiveComponent
from . import ureg
import asyncio
import time

class Sensor(ActiveComponent):
    """A generic sensor.

    Note:
        Users should not directly instantiate an :class:`Sensor` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the Sensor.
        rate (Quantity): Data collection rate in Hz. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 Hz")

    def base_state(self):
        '''Default to being inactive.'''
        return dict(rate="0 Hz")

    def read(self):
        '''Return data to be sent back to the hub.'''
        #Do data collection task here
        data = 2
        return (data, time.time())

    async def update(self):
        '''If data collection is off and needs to be turned on, turn it on.
           If data collection is on and needs to be turned off, turn off and return data.'''
        while ureg.parse_expression(self.rate).to_base_units().magnitude != 0:
            yield self.read()
            await asyncio.sleep(1 / ureg.parse_expression(self.rate).to_base_units().magnitude)
