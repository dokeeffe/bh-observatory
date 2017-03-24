import configparser
import os

import pandas as pd
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint)
from astroplan import Observer, FixedTarget, observability_table
from astroplan import is_observable, is_always_observable
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from mako.template import Template

# Specify conditions and constraints
location = Observer(longitude=-8.2*u.deg, latitude=52.2*u.deg, elevation=100*u.m, name="Obs")
time = Time.now()
sunset = location.sun_set_time(time, which='nearest')
sunrise = location.sun_rise_time(time, which='next')

constraints = [AltitudeConstraint(35*u.deg, 90*u.deg),
               AirmassConstraint(5), AtNightConstraint.twilight_astronomical()]
targets = []
# program_nmo = pd.read_csv('/home/dokeeffe/Downloads/program_nmo.csv')
program_nmo = pd.read_csv('https://www.aavso.org/sites/default/files/legacy/program_nmo.csv')
for row in program_nmo.iterrows():
    coordinates = SkyCoord(row[1]['RA(J2000)'], row[1]['Dec(J2000)'], unit=(u.hourangle, u.deg))
    ft = FixedTarget(name=row[1]['Star name'], coord=coordinates)
    targets.append(ft)

print('Sunset time {}'.format(sunset.iso))
print('Sunrise time {}'.format(sunrise.iso))

time_range = Time([sunset, sunrise])
# Are targets *ever* observable in the time range?
ever_observable = is_observable(constraints, location, targets, time_range=time_range)
# Are targets *always* observable in the time range?
always_observable = is_always_observable(constraints, location, targets, time_range=time_range)

table = observability_table(constraints, location, targets, time_range=time_range)

# add the targets and range details
table['tgt']=targets
table['range']=program_nmo['Range']
table['ra']=program_nmo['RA(J2000)']
table['dec']=program_nmo['Dec(J2000)']
observable = table['ever observable'] == True
visible_targets = table[observable]
high_fraction = visible_targets['fraction of time observable'] > 0.2
visible_targets = visible_targets[high_fraction]
print(visible_targets)

# Now build the list of EKOS JOBS and create the schedule xml file
config = configparser.ConfigParser()
basedir = os.path.dirname(os.path.realpath(__file__))
config.read(basedir + '/ops.cfg')
jobs = []
for row in visible_targets:
    coord = SkyCoord(row['ra'], row['dec'], unit=(u.hourangle, u.deg))
    print('Adding star {} mag range {}'.format(row['target name'],row['range']))
    job = {}
    job['name'] = row['target name']
    job['ra'] = str(coord.ra.hour)
    job['dec'] = str(coord.dec.deg)
    job['sequence'] = config.get('EKOS_SCHEDULING', 'default_sequence_file')
    job['priority'] = 10
    jobs.append(job)
schedule_template = Template(filename=config.get('EKOS_SCHEDULING', 'schedule_template'))
contextDict = {'jobs': jobs}
with open(config.get('EKOS_SCHEDULING', 'target_directory')+"GeneratedSchedule.esl", "w") as text_file:
    text_file.write(schedule_template.render(**contextDict))
print('Generated Schedule File of {} jobs'.format(len(jobs)))


