#!/usr/bin/env python3

import configparser
import csv
import io
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

import os
import logging
import urllib.request
import lxml.html

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


def setup_logging():
    """Configure logging with appropriate format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


class VsxClient:

    def __init__(self):
        pass

    def get_most_recent_measurement(self, star_name: str, band: str, previous_days=90) -> float:
        """
            Get the most recent measurement for a star in a given band from VSX
            :param star_name:
            :param band:
            :param previous_days:
            :return:
            """
        today = Time.now().jd
        from_date = (Time.now() - timedelta(days=previous_days)).jd
        vsx_url = f'https://www.aavso.org/vsx/index.php?view=api.object&ident={urllib.parse.quote(star_name)}&data&csv&minfields&fromjd={from_date}&tojd={today}'
        logging.debug(f'Loading vsx {vsx_url}')
        resp = urllib.request.urlopen(vsx_url)
        data = self._parse_vsx_xml(resp.read().decode('utf-8'))
        for phot in data['csv_data']:
            if phot['band'] == band:
                logging.debug(f'Found V band measurement for {star_name} {phot["mag"]}')
                return float(phot["mag"])
        logging.warning(f'No {band} band measurement found for {star_name}')

    def _parse_vsx_xml(self, xml_string):
        """
            Parse VSX XML string and extract all rows of CSV data from CDATA

            Args:
                xml_string (str): XML string containing VSX data

            Returns:
                dict: Dictionary containing both XML metadata and all CSV data rows
            """
        root = ET.fromstring(xml_string)
        # Get basic XML data
        result = {
            'name': root.find('Name').text,
            'auid': root.find('AUID').text,
            'ra': float(root.find('RA2000').text),
            'dec': float(root.find('Declination2000').text),
            'var_type': root.find('VariabilityType').text,
        }
        cdata = root.find('Data').text
        # Parse all CSV rows from CDATA
        csv_reader = csv.DictReader(io.StringIO(cdata))
        result['csv_data'] = list(csv_reader)
        return result


def determine_capture_sequence(mag):
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


class AavsoEkosScheduleGenerator:
    """
    A tool to generate EKOS schedules from AAVSO's target list
    """
    BRIGHTEST_MAGNITUDE = 9.0
    DIMMEST_MAGNITUDE = 17
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
        self.vsx_client = VsxClient()
        self.api_key = api_key

    def load_aavso_targets(self, obs_section='Alerts / Campaigns'):
        resp = requests.get("https://targettool.aavso.org/TargetTool/api/v1/targets", auth=(self.api_key, "api_token"),
                            params={'obs_section': ['Alerts / Campaigns']})
        result = resp.json()['targets']
        logging.info(f'Loaded {len(result)} targets from AAVSO target tool')
        return result

    def get_observable_stars(self, all_targets):
        time = Time.now()
        sunset = self.location.twilight_evening_astronomical(time, which='nearest')
        sunrise = self.location.twilight_morning_astronomical(time, which='next')
        time_range = Time([sunset, sunrise])

        aavso_targets = sorted(all_targets, key=lambda x: x['star_name'])
        priority_targets = []
        non_priority_targets = []
        for target in aavso_targets:
            if self.photometric_filter_available(target) and self.is_in_magnitude_range(target):
                coordinates = SkyCoord(target["ra"], target["dec"], unit=(u.deg, u.deg))
                ft = FixedTarget(name=target["star_name"], coord=coordinates)
                if target["priority"]:
                    logging.debug(f'Adding {target["star_name"]} to priority targets')
                    priority_targets.append(ft)
                else:
                    logging.debug(f'Adding {target["star_name"]} to non-priority targets')
                    non_priority_targets.append(ft)
            else:
                logging.debug(
                    f'Skipping {target["star_name"]} {target["priority"]} {target["min_mag"]} {target["max_mag"]} {target["filter"]}')
        logging.info(
            f'Filtered {len(aavso_targets)} targets to {len(priority_targets)} priority targets and {len(non_priority_targets)} non-priority targets')

        logging.info(f'Checking observability for {len(priority_targets)} priority targets')
        result = self._filter_observable_tonight(priority_targets, time_range)
        logging.info(f'Checking observability for {len(non_priority_targets)} non-priority targets')
        result += self._filter_observable_tonight(non_priority_targets, time_range)
        logging.info(f'Found {len(result)} observable targets')
        return result

    def _filter_observable_tonight(self, targets, time_range):
        result = []
        priority_table = observability_table(self.constraints, self.location, targets, time_range=time_range)
        observable_targets = priority_table[priority_table['fraction of time observable'] > 0.05]
        logging.info(
            f'There are {len(observable_targets)} targets observable tonight out of {len(targets)}')
        for schedule_entry in observable_targets:
            result.append(schedule_entry['target name'])
        return result

    def photometric_filter_available(self, target):
        logging.debug(
            f'Checking if photometric filter available for {target["star_name"]} {target["filter"]} {target["filter"] == "V"}')
        return target['filter'] in self.AVAILABLE_FILTERS

    def is_in_magnitude_range(self, target):
        magnitude_overlap = self.calculate_magnitude_overlap(target)
        target_overlap_threshold = 0.8
        if target['priority']:
            target_overlap_threshold = 0.4
        logging.debug(
            f'{target["star_name"]} {target["min_mag"]} {target["max_mag"]} overlaps telescope range by {magnitude_overlap*100}%')
        return magnitude_overlap > target_overlap_threshold

    def calculate_magnitude_overlap(self, target):
        """
        Calculate the percentage of target magnitude range that overlaps
        with telescope capabilities.

        Returns: float between 0.0 and 1.0 (or 0.0 if no overlap)
        """
        # Extract target magnitude range
        target_min = target.get('min_mag')
        target_max = target.get('max_mag')

        # If either value is missing, return 0
        if target_min is None or target_max is None:
            return 0.0

        # Calculate overlap boundaries
        # The overlap starts at the brighter (smaller) of the two bright limits
        overlap_bright = max(self.BRIGHTEST_MAGNITUDE, target_max)
        # The overlap ends at the dimmer (larger) of the two dim limits
        overlap_dim = min(self.DIMMEST_MAGNITUDE, target_min)

        # Check if there's any overlap (remember: smaller mag = brighter)
        if overlap_bright >= overlap_dim:
            # No overlap
            return 0.0

        # Calculate the overlap range
        overlap_range = overlap_dim - overlap_bright

        # Calculate the total target range
        target_range = target_min - target_max

        # Avoid division by zero
        if target_range == 0:
            return 1.0 if overlap_range > 0 else 0.0

        # Return percentage overlap
        return overlap_range / target_range

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
        logging.info(f'Building EKOS Schedule for {len(observable)} targets')
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
            recent_mag = self.vsx_client.get_most_recent_measurement(
                row['star_name'], 'V')
            if recent_mag is not None:
                if recent_mag > 18:
                    logging.warning(f'Skipping star {row["star_name"]} as too faint. Mag: {recent_mag}')
                else:
                    job['sequence'] = determine_capture_sequence(recent_mag)
                    logging.info('Using Sequence {} for {} mag {}'.format(
                        job['sequence'], job['name'], recent_mag))
                    job['priority'] = 3
                    jobs.append(job)
            else:
                logging.warning(f'Unable to estimate recent mangnitude for {row["star_name"]}. Skipping')

        schedule_template = Template(filename=os.path.join(os.path.dirname(
            __file__), config.get('EKOS_SCHEDULING', 'schedule_template')))
        contextDict = {'jobs': jobs}
        with open(config.get('EKOS_SCHEDULING', 'target_directory') + "AAVSO-Schedule.esl", "w") as text_file:
            text_file.write(schedule_template.render(**contextDict))
        logging.info('Generated Schedule File of {} jobs to {}'.format(len(jobs), config.get(
            'EKOS_SCHEDULING', 'target_directory') + "AAVSO-Schedule.esl"))


if __name__ == '__main__':
    setup_logging()
    generator = AavsoEkosScheduleGenerator()
    aavso_targets = generator.load_aavso_targets()
    observable_tonight = generator.get_observable_stars(aavso_targets)
    logging.info(f'Observable tonight: {",".join(observable_tonight)}')
    # generator.download_aavso_data(observable_tonight)
    generator.build_ekos_schedule_xml_from_table(aavso_targets, observable_tonight)
