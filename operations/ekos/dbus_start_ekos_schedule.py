import subprocess

import time
from astroplan import Observer, FixedTarget, observability_table, AtNightConstraint
from astropy import units as u
from astropy.time import Time

LONGITUDE = -8.2
LATITUDE = 52.2
ELEVATION = 100

def is_night_time(time):
    polaris = FixedTarget.from_name('Polaris')
    at_night = AtNightConstraint.twilight_civil()
    location = Observer(longitude=LONGITUDE * u.deg, latitude=LATITUDE * u.deg,
                    elevation=ELEVATION * u.m, name="Obs")
    return at_night.compute_constraint(time, location, polaris)

def is_disabled():
    return False

def is_weather_ok():
    return True

def is_telescope_parked():
    return True

def is_roof_closed():
    return True

print(is_night_time(Time.now()) and is_weather_ok())

if(not subprocess.run(['pgrep', '-x', 'indiserver'], stdout=subprocess.PIPE).stdout):
    print('Starting indiserver')
    # subprocess.Popen(['kstars'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print('started')
    time.sleep(2)


if(not subprocess.run(['pgrep', '-x', 'kstars'], stdout=subprocess.PIPE).stdout):
    print('Starting Kstars')
    subprocess.Popen(['kstars'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print('started')
    time.sleep(2)

base_command = ['dbus-send', '--session', '--print-reply', '--dest=org.kde.kstars']
result = subprocess.run(base_command + ['/kstars/MainWindow_1/actions/ekos', 'org.qtproject.Qt.QAction.trigger'], stdout=subprocess.PIPE)
# result = subprocess.run(base_command + ['/KStars/Ekos', 'org.kde.kstars.Ekos.start'], stdout=subprocess.PIPE)
# result = subprocess.run(base_command + ['/KStars/Ekos/Scheduler', 'org.kde.kstars.Ekos.Scheduler.loadScheduler', 'string:/home/dokeeffe/Dropbox/EkosSchedules/AAVSO-Schedule.esl'], stdout=subprocess.PIPE)
# result = subprocess.run(base_command + ['/KStars/Ekos/Scheduler', 'org.kde.kstars.Ekos.Scheduler.start'], stdout=subprocess.PIPE)

#TODO: Switch off IR lamps in camera
#TODO: Switch off Dehumidifier
#TODO: Send SMS