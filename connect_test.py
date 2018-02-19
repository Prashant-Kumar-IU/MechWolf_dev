from components import ViciValve
from connection import DeviceExecutor

import sys
import Pyro4
import Pyro4.util

sys.excepthook = Pyro4.util.excepthook


with ViciValve(name="hi") as v:
    v.connect('/dev/tty.usbserial')
    e = Pyro4.Proxy("PYRONAME:de")
    for i in range(100):
        e.submit(v, i, v.set_position, (i%9)+1)
    e.submit(v, 4.5, v.set_position, 8)
    print (e._task_queue)
    e.run()