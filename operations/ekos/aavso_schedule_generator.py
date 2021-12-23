#!/usr/bin/env python3

import configparser
import re

import os

import urllib.request
import lxml.html

import numpy
import pandas as pd
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint)
from astroplan import Observer, FixedTarget, observability_table
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from mako.template import Template
from datetime import datetime
from datetime import timedelta
from astropy.utils.iers import conf
conf.auto_max_age = None

class WebopsClient:

    def __init__(self):
        pass

    def _load_page(self, page, star, start, end):
        params = {'start': start, 'end': end, 'num_results': 100, 'obs_types': 'ccd', 'star': star, 'page': page}
        url = 'https://aavso.org/apps/webobs/results/?' + urllib.parse.urlencode(params)
        print(url)
        fp = urllib.request.urlopen(url)
        tree = lxml.html.fromstring(fp.read())
        rows = tree.xpath('//table[@class="observations"]/tbody/tr')
        return rows

    def _find_first_matching_filter(self, rows, filt):
        for row in rows:
            values = [col.text_content() for col in row]
            if len(values) > 6:
                mag = values[4]
                photo_filter = values[6]
                if photo_filter == filt:
                    return mag

    def get_most_recent_measurement(self, star, filt):
        page = 1
        start = datetime.now() - timedelta(days=10)
        end = datetime.now()
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        while page < 10:
            try:
                rows = self._load_page(page, star, start_str, end_str)
            except:
                print('ERROR loading page')
                return
            measure = self._find_first_matching_filter(rows, filt)
            if measure is not None:
                return float(measure.replace('<',''))
            else:
                page+=1

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
        self.webops_client = WebopsClient()

    def load_aavso_data_and_filter(self):
        '''
        Load AAVSO data and filter out objects not visible tonight
        :return: `~astropy.table.Table` An astropy table of visible targets
        '''
        targets = []
        print('loading from aavso {}'.format(self.AAVSO_TARGET_URL))
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
        # print(visible_targets)

        filtered = list(filter(self.is_candidate_for_observation, table))
        print('Filtered a total of {} targets down to {} observable'.format(len(table), len(filtered)))
        return filtered

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
            coord = SkyCoord(row['ra'], row['dec'], unit=(u.hourangle, u.deg))
            job = {}
            job['name'] = row['target name']
            job['ra'] = str(coord.ra.hour)
            job['dec'] = str(coord.dec.deg)
            recent_mag = self.webops_client.get_most_recent_measurement(row['target name'], 'V')
            if recent_mag is not None:
                job['sequence'] = self.determine_capture_sequence(recent_mag)
                print('Using Sequence {} for {} mag {}'.format(job['sequence'],job['name'], recent_mag))
                job['priority'] = 1
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
        maxmag = re.findall("\d+\.\d+", aavso_target['maxmag'])
        if coord.dec.deg < 90 \
                and aavso_target['filter'] in self.AVAILABLE_FILTERS \
                and aavso_target['ever observable'] == True and aavso_target['fraction of time observable'] > 0.25 \
                and maxmag and maxmag[0] and float(maxmag[0]) > self.MAX_MAGNITUDE:
            print('Star {} is candidate for observation. filter:{} Observable {} of night'
                  .format(aavso_target['target name'],aavso_target['filter'], aavso_target['fraction of time observable']))
            return True
        else:
            # print('Star {} filter {} is not a candidate, observable {} of night'
            #       .format(aavso_target['target name'],aavso_target['filter'], aavso_target['fraction of time observable']))
            return False

    def determine_capture_sequence(self, mag):
        print(f'Determining best sequence for mag {mag}')
        if mag > 15.0:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x300PV.esq'
        if mag > 13.5:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x240PV.esq'
        if mag > 12.5:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x120PV.esq'
        if mag > 11.0:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x60PV.esq'
        else:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x20PV.esq'


if __name__ == '__main__':
    generator = AavsoEkosScheduleGenerator()
    generator.build_ekos_schedule_xml_from_table(generator.load_aavso_data_and_filter())
