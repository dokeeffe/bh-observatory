import configparser
import os, subprocess

from mako.template import Template
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord


def generate_schedule_from_aavso_objects():
    '''
    Generates an EKOS sequence file from AAVSO's list of stars in need of observation.
    :return:
    '''
    config = configparser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    jobs = []
    df = pd.read_csv(config.get('EKOS_SCHEDULING', 'aavso_url'))
    print(df)
    print('loaded AAVSO list of stars in need of observation')
    for row in df.iterrows():
        coord = SkyCoord(row[1]['RA(J2000)'], row[1]['Dec(J2000)'], unit=(u.hourangle, u.deg))
        if (coord.dec.deg > int(config.get('EKOS_SCHEDULING', 'declination_limit_filter')) and '***' not in row[1]['Star name']):
            print('Adding star {} mag range {}'.format(row[1]['Star name'],row[1]['Range']))
            job = {}
            job['name'] = row[1]['Star name']
            # print(row[1]['Range'])
            job['ra'] = str(coord.ra.deg)
            job['dec'] = str(coord.dec.deg)
            job['sequence'] = config.get('EKOS_SCHEDULING', 'default_sequence_file')
            job['priority'] = 10
            jobs.append(job)
    schedule_template = Template(filename='templates/schedule_template.esl')
    contextDict = {'jobs': jobs}
    with open(config.get('EKOS_SCHEDULING', 'target_directory')+"GeneratedSchedule.esl", "w") as text_file:
        text_file.write(schedule_template.render(**contextDict))
    print('Generated Schedule File')


if __name__ == '__main__':
    generate_schedule_from_aavso_objects()
    subprocess.call(['dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.loadScheduler string:"/home/dokeeffe/Dropbox/EkosSchedules/GeneratedSchedule.esl"'], shell=True)
    subprocess.call(['dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.start'], shell=True)
