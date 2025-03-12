#!/usr/bin/env python3

import configparser
import re
import requests

import os
import logging

import urllib.request
import lxml.html

import numpy
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
        params = {'num_results': 25, 'obs_types': 'ccd', 'star': star}
        url = 'https://aavso.org/apps/webobs/results/?' + urllib.parse.urlencode(params)
        logging.info(url)
        # Create headers dictionary with User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0'
        }
        # Create a Request object with the URL and headers
        request = urllib.request.Request(url, headers=headers)

        # Open the URL with the custom request
        fp = urllib.request.urlopen(request)
        tree = lxml.html.fromstring(fp.read())
        rows = tree.xpath('//table[@class="observations"]/tbody/tr')
        logging.info(f'Got {len(rows)} rows')
        return rows


    def _load_page_deprecated(self, page, star, start, end):
        #params = {'start': start, 'end': end, 'num_results': 100, 'obs_types': 'ccd', 'star': star, 'page': page}
        params = {'num_results': 25, 'obs_types': 'ccd', 'star': star}
        url = 'https://aavso.org/apps/webobs/results/?' + \
            urllib.parse.urlencode(params)
        logging.info(url)
        fp = urllib.request.urlopen(url)
        tree = lxml.html.fromstring(fp.read())
        rows = tree.xpath('//table[@class="observations"]/tbody/tr')
        logging.info(f'Got {len(rows)} rows')
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
        while page < 2:
            try:
                rows = self._load_page(page, star, start_str, end_str)
            except Exception as e:
                logging.exception('ERROR loading page')
                return
            measure = self._find_first_matching_filter(rows, filt)
            if measure is not None:
                return float(measure.replace('<', ''))
            else:
                page += 1


class AavsoEkosScheduleGenerator:
    '''
    A tool to generate EKOS schedules from AAVSO's target list https://filtergraph.com/aavso
    '''
    MAX_MAGNITUDE = 9.0
    MIN_MAGNITUDE = 17
    DEFAULT_LONGITUDE = -8.2
    DEFAULT_LATITUDE = 52.2
    DEFAULT_ELEVATION = 100
    AVAILABLE_FILTERS = ['V', 'All']
    MIN_TARGET_ALTITUDE_DEG = 35
    GUESS_SEQUENCE_FOR_UNKNOWN_MAG = False
    API_KEY = os.environ['AAVSO_API_KEY']

    def __init__(self, lat=DEFAULT_LATITUDE, lon=DEFAULT_LONGITUDE, elevation=DEFAULT_ELEVATION,
                 min_target_altitude_deg=MIN_TARGET_ALTITUDE_DEG, api_key=API_KEY):
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
        self.api_key = api_key

    

    def load_aavso_data(self, obs_section='Alerts / Campaigns'):
            resp = requests.get("https://targettool.aavso.org/TargetTool/api/v1/targets",auth=(self.api_key,"api_token"),params={'obs_section':['Alerts / Campaigns']})
            return resp.json()['targets']
    
    def get_observable_stars(self, all_targets):
        result = []
       
        time = Time.now()
        sunset = self.location.twilight_evening_astronomical(time, which='nearest')
        sunrise = self.location.twilight_morning_astronomical(time, which='next')
        time_range = Time([sunset, sunrise])
        
        
        aavso_targets = sorted(all_targets, key=lambda x: x['star_name'])
        targets = []
        for target in aavso_targets:
            if target["priority"] and (target['filter'] == 'V' or target['filter'] == 'All' )and target['min_mag'] and target['min_mag'] < self.MIN_MAGNITUDE and target['max_mag'] > self.MAX_MAGNITUDE:
                coordinates = SkyCoord(target["ra"], target["dec"], unit=(u.deg, u.deg))
                logging.info(f'{target["star_name"]} {coordinates}')
                ft = FixedTarget(name=target["star_name"], coord=coordinates)
                targets.append(ft)
        
        table = observability_table(self.constraints, self.location, targets, time_range=time_range)

        for schedule_entry in table[table['fraction of time observable'] > 0.05]:
            result.append(schedule_entry['target name'])
        return result
    
    def _find(self, star, all_targets):
        for tgt in all_targets:
            if tgt['star_name'] == star:
                return tgt

    def build_ekos_schedule_xml_from_table(self, all_targets, observable):
        '''
        Build an EKOS schedule from an astropy table of targets.
        :param all_targets:
        :param observable
        :return:
        '''
        config = configparser.ConfigParser()
        basedir = os.path.dirname(os.path.realpath(__file__))
        config.read(basedir + '/ops.cfg')
        jobs = []

        for star in observable:
            row = self._find(star, all_targets)
            coord = SkyCoord(row['ra'], row['dec'], unit=(u.deg, u.deg))
            job = {}
            job['name'] = row['star_name']
            job['ra'] = str(coord.ra.hour)
            job['dec'] = str(coord.dec.deg)
            recent_mag = self.webops_client.get_most_recent_measurement(
                row['star_name'], 'V')
            if recent_mag is not None:
                if recent_mag > 18:
                    logging.info(f'Skipping star as too faint. Mag: {recent_mag}')
                else:
                    job['sequence'] = self.determine_capture_sequence(recent_mag)
                    logging.info('Using Sequence {} for {} mag {}'.format(
                        job['sequence'], job['name'], recent_mag))
                    job['priority'] = 3
                    jobs.append(job)
            else:
                logging.warning('Unable to estimate recent mangnitude. Skipping')

        schedule_template = Template(filename=os.path.join(os.path.dirname(
            __file__), config.get('EKOS_SCHEDULING', 'schedule_template')))
        contextDict = {'jobs': jobs}
        with open(config.get('EKOS_SCHEDULING', 'target_directory') + "AAVSO-Schedule.esl", "w") as text_file:
            text_file.write(schedule_template.render(**contextDict))
        logging.info('Generated Schedule File of {} jobs to {}'.format(len(jobs), config.get(
            'EKOS_SCHEDULING', 'target_directory') + "AAVSO-Schedule.esl"))

    def determine_capture_sequence(self, mag):
        logging.info(f'Determining best sequence for mag {mag}')
        if mag > 15.0:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/3x300PV.esq'
        if mag > 13.5:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/3x240PV.esq'
        if mag > 12.5:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/4x120PV.esq'
        if mag > 11.0:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x60PV.esq'
        else:
            return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x20PV.esq'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    generator = AavsoEkosScheduleGenerator()
    aavso_targets = generator.load_aavso_data()
    observable = generator.get_observable_stars(aavso_targets)
    generator.build_ekos_schedule_xml_from_table(aavso_targets, observable)

