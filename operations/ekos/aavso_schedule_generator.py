#!/usr/bin/env python3

import configparser
import re

import os

import numpy
import pandas as pd
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint)
from astroplan import Observer, FixedTarget, observability_table
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from mako.template import Template

from astropy.utils.iers import conf
conf.auto_max_age = None

class AavsoEkosScheduleGenerator:
    '''
    A tool to generate EKOS schedules from AAVSO's target list https://filtergraph.com/aavso
    '''
    MAX_MAGNITUDE = 9.0
    DEFAULT_LONGITUDE = -8.2
    DEFAULT_LATITUDE = 52.2
    DEFAULT_ELEVATION = 100
    AVAILABLE_FILTERS = ['V', 'All']
    MIN_TARGET_ALTITUDE_DEG = 40
    AAVSO_TARGET_URL = 'https://filtergraph.com/aavso/default/index.csv?ac=on&settype=true'

    def __init__(self, lat=DEFAULT_LATITUDE, lon=DEFAULT_LONGITUDE, elevation=DEFAULT_ELEVATION,
                 min_target_altitude_deg=MIN_TARGET_ALTITUDE_DEG):
        '''
        Constructor, defaults for location can be overriden. Build conditions and constraints for today and current location.
        :param lat:
        :param lon:
        :param elevation:
        :param min_target_altitude_deg:
        '''
        self.location = Observer(longitude=lon * u.deg, latitude=lat * u.deg,
                                 elevation=elevation * u.m, name="Obs")
        self.time = Time.now()
        self.constraints = [AltitudeConstraint(min_target_altitude_deg * u.deg, 90 * u.deg),
                            AirmassConstraint(5), AtNightConstraint.twilight_nautical()]
        sunset = self.location.sun_set_time(self.time, which='nearest')
        sunrise = self.location.sun_rise_time(self.time, which='next')
        self.time_range = Time([sunset, sunrise])

    def load_aavso_data_and_filter(self):
        '''
        Load AAVSO data and filter out objects not visible tonight
        :return: `~astropy.table.Table` An astropy table of visible targets
        '''
        targets = []
        target_csv_data = pd.read_csv(self.AAVSO_TARGET_URL)
        for row in target_csv_data.iterrows():
            coordinates = SkyCoord(row[1]['RA (J2000.0)'], row[1]['Dec (J2000.0)'], unit=(u.hourangle, u.deg))
            ft = FixedTarget(name=row[1]['Star Name'], coord=coordinates)
            targets.append(ft)

        table = observability_table(self.constraints, self.location, targets, time_range=self.time_range)
        # add the targets and range details
        table['tgt'] = targets
        table['minmag'] = target_csv_data['Min Mag']
        table['maxmag'] = target_csv_data['Max Mag']
        table['filter'] = target_csv_data['Filter/Mode']
        table['ra'] = target_csv_data['RA (J2000.0)']
        table['dec'] = target_csv_data['Dec (J2000.0)']

        # filter by observable
        observable = table['ever observable'] == True
        visible_targets = table[observable]
        high_fraction = visible_targets['fraction of time observable'] > 0.2
        visible_targets = visible_targets[high_fraction]
        print('Filtered a total of {} targets down to {} observable'.format(len(table), len(visible_targets)))
        # print(visible_targets)

        return table

    def build_ekos_schedule_xml_from_table(self, visible_targets):
        '''
        Build an EKOS schedule from an astropy table of targets.
        :param visible_targets:
        :return:
        '''
        config = configparser.ConfigParser()
        basedir = os.path.dirname(os.path.realpath(__file__))
        config.read(basedir + '/ops.cfg')
        jobs = []
        for row in visible_targets:
            if self.is_candidate_for_observation(row):
                coord = SkyCoord(row['ra'], row['dec'], unit=(u.hourangle, u.deg))
                minmag = re.findall("\d+\.\d+", row['minmag'])
                maxmag = re.findall("\d+\.\d+", row['maxmag'])
                minmag = float(minmag[0]) if len(minmag) > 0 else numpy.nan
                maxmag = float(maxmag[0]) if len(maxmag) > 0 else numpy.nan
                job = {}
                job['name'] = row['target name']
                job['ra'] = str(coord.ra.hour)
                job['dec'] = str(coord.dec.deg)
                job['sequence'] = self.determine_capture_sequence(config, minmag, maxmag)
                print('            Sequence {}'.format(job['sequence']))
                job['priority'] = 6
                jobs.append(job)
        schedule_template = Template(filename=os.path.join(os.path.dirname(__file__), config.get('EKOS_SCHEDULING', 'schedule_template')))
        contextDict = {'jobs': jobs}
        with open(config.get('EKOS_SCHEDULING', 'target_directory') + "AAVSO-Schedule.esl", "w") as text_file:
            text_file.write(schedule_template.render(**contextDict))
        print('Generated Schedule File of {} jobs to {}'.format(len(jobs), config.get('EKOS_SCHEDULING', 'target_directory') + "AAVSO-Schedule.esl"))

    def is_candidate_for_observation(self, aavso_target):
        '''
        Returns true id the target passed is a candidate for observation. It must be visible from current location and not too close to the pole and the requested filter be one of ours
        :param aavso_target:
        :return:
        '''
        coord = SkyCoord(aavso_target['ra'], aavso_target['dec'], unit=(u.hourangle, u.deg))
        minmag = re.findall("\d+\.\d+", aavso_target['minmag'])
        maxmag = re.findall("\d+\.\d+", aavso_target['maxmag'])
        if coord.dec.deg < 80 \
                and aavso_target['filter'] in self.AVAILABLE_FILTERS \
                and aavso_target['ever observable'] == True and aavso_target['fraction of time observable'] > 0.25 \
                and maxmag and maxmag[0] and float(maxmag[0]) > self.MAX_MAGNITUDE:
            print('Adding star {} mag range {}-{} filter:{} which is observable {} of night'
                  .format(aavso_target['target name'], minmag, maxmag,aavso_target['filter'], aavso_target['fraction of time observable']))
            return True
        else:
            print('Skipping star {} mag range {}-{} filter:{} which is observable {} of night'
                  .format(aavso_target['target name'], minmag, maxmag,aavso_target['filter'], aavso_target['fraction of time observable']))
            return False

    def determine_capture_sequence(self, config, minmag, maxmag):
        '''
        Determine the EKOS capture sequence to use based on the brightness of the target.
        TODO: update this to be better as some are saturated
               Examples AG Dra mag 9.8 was 56000 adu in 60sec
               FIPer 16.8 TARGET STAR PEAK FLUX 1612.774070511463 exposure was 240.0 sec
                RMon 12.2 TARGET STAR PEAK FLUX 14281.233385386071 exposure was 120.0 sec
                TTAri 10.7-11  TARGET STAR PEAK FLUX 59491.81185169168 exposure was 120.0 sec *
                SUUMa 14.25 TARGET STAR PEAK FLUX 4178.004539432007 exposure was 120.0 sec
                V378 Peg 14.0 TARGET STAR PEAK FLUX 3226.335193173021 exposure was 120.0 sec
                9.6 TARGET STAR PEAK FLUX 63458.85411067805 OUTSIDE LINEAR RANGE exposure was 60.0 sec
                14.1 ARGET STAR PEAK FLUX 4384.823487265183 exposure was 120.0 sec
yo
        :param config:
        :param minmag:
        :param maxmag:
        :return:
        '''
        if numpy.isnan(maxmag) or numpy.isnan(maxmag):
            return '/home/dokeeffe/Dropbox/EkosSequences/imaging/photometry/5x60PV.esq'
        if (minmag + maxmag)/2 > 14.5:
            return '/home/dokeeffe/Dropbox/EkosSequences/imaging/photometry/5x240PV.esq'
        if (minmag + maxmag)/2 > 12:
            return '/home/dokeeffe/Dropbox/EkosSequences/imaging/photometry/5x120PV.esq'
        else:
            return '/home/dokeeffe/Dropbox/EkosSequences/imaging/photometry/5x60PV.esq'


if __name__ == '__main__':
    generator = AavsoEkosScheduleGenerator()
    generator.build_ekos_schedule_xml_from_table(generator.load_aavso_data_and_filter())
