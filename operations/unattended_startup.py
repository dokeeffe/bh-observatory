#import gobject
import os
import logging
import time
from dbus import glib
glib.init_threads()
import dbus


def check_kstars_running(bus):
    try:
        kstars = bus.get_object("org.kde.kstars", "/KStars")
        main_window = dbus.Interface(kstars, 'org.kde.KMainWindow')
        main_window.activateAction('ekos')
    except Exception:
        raise Exception('Cannot connect to kstars, is it running?')


def open_ekos_window(bus):
    kstars = bus.get_object("org.kde.kstars", "/KStars")
    main_window = dbus.Interface(kstars, 'org.kde.KMainWindow')
    main_window.activateAction('ekos')


def check_weather():
    pass


def check_schedule_exists():
    pass


def check_nighttime():
    pass


def check_roof_closed():
    pass


def check_scope_parked():
    pass


def check_override_flag():
    pass


def check_indiserver_running():
    pass


def check_power_on():
    pass


def perform_checks(bus):
    check_schedule_exists()
    check_weather()
    check_nighttime()
    check_roof_closed()
    check_scope_parked()
    check_override_flag()
    check_kstars_running(bus)
    check_indiserver_running()
    check_power_on()


def start_scheduler(bus):
    remote_object = bus.get_object("org.kde.kstars", "/KStars/Ekos/Scheduler")
    logging.debug(remote_object.Introspect())
    iface = dbus.Interface(remote_object, 'org.kde.kstars.Ekos.Scheduler')
    iface.loadScheduler('/home/okeefd3/Desktop/schedule.esl')
    iface.start()


def main():
    bus = dbus.SessionBus()
    perform_checks(bus)
    open_ekos_window(bus)
    start_scheduler(bus)


if __name__ == '__main__':
    main()
