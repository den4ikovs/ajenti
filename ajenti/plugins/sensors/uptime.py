import os
import psutil
import time

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.util import str_timedelta


def get_proc_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])
    except IOError as e:
        raise e


@plugin
class UnixUptimeSensor(Sensor):
    id = 'uptime'
    timeout = 1

    def measure(self, variant):
        if os.path.isfile('/proc/uptime'):
            return get_proc_uptime()
        return time.time() - psutil.BOOT_TIME


@plugin
class UptimeWidget(DashboardWidget):
    name = _('Uptime')
    icon = 'off'

    def init(self):
        self.sensor = Sensor.find('uptime')
        self.append(self.ui.inflate('sensors:value-widget'))

        self.find('icon').text = 'off'
        self.find('name').text = 'Uptime'
        self.find('value').text = str_timedelta(self.sensor.value())
