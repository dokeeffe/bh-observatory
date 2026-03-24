#!/usr/bin/env python3
"""
Interactive AAVSO EKOS Schedule Generator

Builds an EKOS observation schedule from:
  - AAVSO Target Tool API  (optional)
  - Manually entered star names, e.g. from alert emails  (optional)
  - Or a combination of both

Usage:
    python aavso_interactive_scheduler.py
"""

import configparser
import csv
import io
import re
import urllib.parse
import xml.etree.ElementTree as ET

import requests
import os
import logging

from astroplan import AltitudeConstraint, AirmassConstraint, AtNightConstraint
from astroplan import Observer, FixedTarget, observability_table
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from mako.template import Template
from datetime import datetime, timezone, timedelta
from astropy.utils.iers import conf

conf.auto_max_age = None


def setup_logging(level):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# ---------------------------------------------------------------------------
# VSX client
# ---------------------------------------------------------------------------

class VsxClient:

    def lookup_star(self, star_name: str) -> dict | None:
        """Return basic star info (name, ra, dec, var_type) from VSX, or None on failure."""
        url = f'https://www.aavso.org/vsx/index.php?view=api.object&ident={urllib.parse.quote(star_name)}&data&csv&minfields'
        logging.debug(f'VSX lookup: {url}')
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            return self._parse_vsx_xml(resp.text)
        except Exception as e:
            logging.error(f'VSX lookup failed for "{star_name}": {e}')
            return None

    def get_most_recent_measurement(self, star_name: str, band: str) -> float | None:
        """Return the most recent magnitude for star_name in the given band, or None."""
        data = self.lookup_star(star_name)
        if data is None:
            return None
        for phot in data.get('csv_data', []):
            if phot.get('band') == band:
                logging.debug(f'Most recent {band} mag for {star_name}: {phot["mag"]}')
                return float(phot['mag'])
        logging.warning(f'No {band} band measurement found for {star_name}')
        return None

    def _parse_vsx_xml(self, xml_string: str) -> dict:
        root = ET.fromstring(xml_string)
        result = {
            'name':     root.find('Name').text,
            'auid':     root.find('AUID').text,
            'ra':       float(root.find('RA2000').text),
            'dec':      float(root.find('Declination2000').text),
            'var_type': root.find('VariabilityType').text,
        }
        cdata = root.find('Data').text
        csv_reader = csv.DictReader(io.StringIO(cdata))
        result['csv_data'] = list(csv_reader)
        return result


# ---------------------------------------------------------------------------
# Sequence selection
# ---------------------------------------------------------------------------

def determine_capture_sequence(mag: float) -> str:
    if mag > 15.0:
        return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/3x300PV.esq'
    if mag > 13.5:
        return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/3x240PV.esq'
    if mag > 12.5:
        return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/4x120PV.esq'
    if mag > 11.0:
        return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x60PV.esq'
    return '/home/dokeeffe/pCloudDrive/EkosSequences/imaging/photometry/5x20PV.esq'


# ---------------------------------------------------------------------------
# Main scheduler
# ---------------------------------------------------------------------------

class AavsoEkosScheduleGenerator:
    BRIGHTEST_MAGNITUDE = 9.0
    DIMMEST_MAGNITUDE = 17
    DEFAULT_LONGITUDE = -8.2
    DEFAULT_LATITUDE = 52.2
    DEFAULT_ELEVATION = 100
    AVAILABLE_FILTERS = ['V', 'All']
    MIN_TARGET_ALTITUDE_DEG = 35
    EXCLUDE_LIST = ['ASAS J060415+1245.9']

    def __init__(self, lat=DEFAULT_LATITUDE, lon=DEFAULT_LONGITUDE,
                 elevation=DEFAULT_ELEVATION,
                 min_target_altitude_deg=MIN_TARGET_ALTITUDE_DEG):
        self.location = Observer(longitude=lon * u.deg, latitude=lat * u.deg,
                                 elevation=elevation * u.m, name="Obs")
        self.time = Time.now()
        self.constraints = [
            AltitudeConstraint(min_target_altitude_deg * u.deg, 90 * u.deg),
            AirmassConstraint(5),
            AtNightConstraint.twilight_nautical(),
        ]
        self.vsx_client = VsxClient()
        self.api_key = os.environ['AAVSO_API_KEY']

    # ------------------------------------------------------------------ #
    # Data loading
    # ------------------------------------------------------------------ #

    def load_aavso_targets(self) -> list[dict]:
        resp = requests.get(
            'https://targettool.aavso.org/TargetTool/api/v1/targets',
            auth=(self.api_key, 'api_token'),
            params={'obs_section': ['Alerts / Campaigns']},
        )
        resp.raise_for_status()
        targets = resp.json()['targets']
        logging.info(f'Loaded {len(targets)} targets from AAVSO Target Tool')
        return targets

    def build_manual_target(self, star_name: str) -> dict | None:
        """
        Look up a star in VSX by name and return a target dict compatible with
        the rest of the pipeline.  Returns None if the star cannot be found.
        """
        info = self.vsx_client.lookup_star(star_name)
        if info is None:
            logging.error(f'Could not find "{star_name}" in VSX — skipping')
            return None
        target = {
            'star_name':      info['name'],
            'ra':             info['ra'],
            'dec':            info['dec'],
            'filter':         'V',
            'priority':       True,
            'min_mag':        None,
            'max_mag':        None,
            'last_data_point': datetime.now(timezone.utc).timestamp(),
            'other_info':     'Manually added',
            '_manual':        True,   # bypass magnitude-range / recency filters
        }
        logging.info(f'Resolved manual target "{star_name}" → ra={info["ra"]:.4f}, dec={info["dec"]:.4f}')
        return target

    # ------------------------------------------------------------------ #
    # Filtering helpers
    # ------------------------------------------------------------------ #

    def _months_since_last_data(self, target) -> int:
        if target['last_data_point'] is None:
            return 9_999_999
        last = datetime.fromtimestamp(target['last_data_point'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        months = (now.year - last.year) * 12 + (now.month - last.month)
        if now.day < last.day:
            months -= 1
        return months

    def _extract_alert_notice(self, target) -> int | None:
        text = target.get('other_info', '')
        match = re.search(r'Alert Notice (\d+)', text)
        return int(match.group(1)) if match else None

    def photometric_filter_available(self, target) -> bool:
        return target['filter'] in self.AVAILABLE_FILTERS

    def is_in_magnitude_range(self, target) -> bool:
        target_min = target.get('min_mag')
        target_max = target.get('max_mag')
        if target_min is None or target_max is None:
            return False
        overlap_bright = max(self.BRIGHTEST_MAGNITUDE, target_max)
        overlap_dim = min(self.DIMMEST_MAGNITUDE, target_min)
        if overlap_bright >= overlap_dim:
            return False
        overlap_range = overlap_dim - overlap_bright
        target_range = target_min - target_max
        if target_range == 0:
            return overlap_range > 0
        overlap_fraction = overlap_range / target_range
        threshold = 0.4 if target.get('priority') else 0.8
        return overlap_fraction > threshold

    def _filter_observable_tonight(self, targets: list[FixedTarget],
                                   time_range) -> list[str]:
        if not targets:
            return []
        table = observability_table(self.constraints, self.location, targets,
                                    time_range=time_range)
        observable = table[table['fraction of time observable'] > 0.05]
        logging.info(f'{len(observable)} / {len(targets)} targets observable tonight')
        return [row['target name'] for row in observable]

    # ------------------------------------------------------------------ #
    # Observable targets
    # ------------------------------------------------------------------ #

    def get_observable_stars(self, all_targets: list[dict],
                             months_old_data_threshold: int = 2) -> list[str]:
        time = Time.now()
        sunset = self.location.twilight_evening_astronomical(time, which='nearest')
        sunrise = self.location.twilight_morning_astronomical(time, which='next')
        time_range = Time([sunset, sunrise])

        candidates = sorted(
            [t for t in all_targets if t['star_name'] not in self.EXCLUDE_LIST],
            key=lambda x: x['star_name'],
        )

        priority_targets = []
        non_priority_targets = []

        for target in candidates:
            is_manual = target.get('_manual', False)

            if is_manual:
                # Manual targets bypass magnitude-range and recency checks
                coord = SkyCoord(target['ra'], target['dec'], unit=(u.deg, u.deg))
                ft = FixedTarget(name=target['star_name'], coord=coord)
                logging.info(f'Manual target {target["star_name"]} added directly to priority list')
                priority_targets.append(ft)
                continue

            # Normal AAVSO target filtering
            months_since = self._months_since_last_data(target)
            if (self.photometric_filter_available(target)
                    and self.is_in_magnitude_range(target)
                    and months_since <= months_old_data_threshold):
                coord = SkyCoord(target['ra'], target['dec'], unit=(u.deg, u.deg))
                ft = FixedTarget(name=target['star_name'], coord=coord)
                notice = self._extract_alert_notice(target)
                if target.get('priority'):
                    logging.info(f'Priority: {target["star_name"]} (notice={notice}, data age={months_since}mo)')
                    priority_targets.append(ft)
                else:
                    logging.info(f'Normal: {target["star_name"]} (notice={notice}, data age={months_since}mo)')
                    non_priority_targets.append(ft)
            else:
                logging.debug(f'Skipping {target["star_name"]} — filter/mag/recency check failed')

        logging.info(f'Candidates: {len(priority_targets)} priority, {len(non_priority_targets)} normal')

        result = self._filter_observable_tonight(priority_targets, time_range)
        result += self._filter_observable_tonight(non_priority_targets, time_range)
        logging.info(f'*** {len(result)} observable targets tonight ***')
        return result

    # ------------------------------------------------------------------ #
    # Schedule generation
    # ------------------------------------------------------------------ #

    def _find(self, star_name: str, all_targets: list[dict]) -> dict | None:
        for t in all_targets:
            if t['star_name'] == star_name:
                return t
        return None

    def build_ekos_schedule(self, all_targets: list[dict], observable: list[str]):
        logging.info(f'Building EKOS schedule for {len(observable)} targets')
        config = configparser.ConfigParser()
        basedir = os.path.dirname(os.path.realpath(__file__))
        config.read(os.path.join(basedir, 'ops.cfg'))

        jobs = []
        for star in observable:
            row = self._find(star, all_targets)
            if row is None:
                logging.warning(f'Could not find target data for {star} — skipping')
                continue
            coord = SkyCoord(row['ra'], row['dec'], unit=(u.deg, u.deg))
            recent_mag = self.vsx_client.get_most_recent_measurement(star, 'V')
            if recent_mag is None:
                if row.get('_manual'):
                    recent_mag = _prompt_manual_magnitude(star)
                if recent_mag is None:
                    logging.warning(f'No recent V magnitude for {star} — skipping')
                    continue
            if recent_mag > 18:
                logging.warning(f'Skipping {star}: too faint (mag={recent_mag})')
                continue
            job = {
                'name':     row['star_name'],
                'ra':       str(coord.ra.hour),
                'dec':      str(coord.dec.deg),
                'sequence': determine_capture_sequence(recent_mag),
                'priority': 3,
            }
            logging.info(f'{star}: mag={recent_mag:.1f} → {os.path.basename(job["sequence"])}')
            jobs.append(job)

        template_path = os.path.join(basedir,
                                     config.get('EKOS_SCHEDULING', 'schedule_template'))
        schedule_template = Template(filename=template_path)
        output_path = config.get('EKOS_SCHEDULING', 'target_directory') + 'AAVSO-Schedule.esl'
        with open(output_path, 'w') as f:
            f.write(schedule_template.render(jobs=jobs))
        logging.info(f'Wrote {len(jobs)}-job schedule to {output_path}')


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def _prompt_manual_magnitude(star_name: str) -> float | None:
    """Ask the user to supply a V magnitude for a star when VSX has no recent data."""
    print(f'\n  No recent V magnitude found in VSX for "{star_name}".')
    while True:
        answer = input(f'  Enter V magnitude manually (or press Enter to skip): ').strip()
        if answer == '':
            return None
        try:
            mag = float(answer)
            logging.info(f'Using manually entered magnitude {mag} for {star_name}')
            return mag
        except ValueError:
            print('  Invalid value — please enter a number (e.g. 14.2).')


def prompt_yes_no(question: str, default: bool) -> bool:
    hint = '[Y/n]' if default else '[y/N]'
    while True:
        answer = input(f'{question} {hint}: ').strip().lower()
        if answer == '':
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print('  Please enter y or n.')


def collect_manual_stars() -> list[str]:
    print('\nEnter star names one per line (e.g. "RW Aur", "YZ Cnc").')
    print('Press Enter on an empty line when done.\n')
    names = []
    while True:
        name = input('  Star name: ').strip()
        if not name:
            break
        names.append(name)
    return names


def main():
    setup_logging(logging.INFO)

    print('=' * 60)
    print('  AAVSO EKOS Interactive Schedule Generator')
    print('=' * 60)

    load_api = prompt_yes_no('\nLoad targets from AAVSO Target Tool API?', default=True)
    add_manual = prompt_yes_no('Manually add star names?', default=False)

    if not load_api and not add_manual:
        print('Nothing to do. Exiting.')
        return

    generator = AavsoEkosScheduleGenerator()
    all_targets: list[dict] = []

    if load_api:
        print('\nFetching targets from AAVSO Target Tool...')
        all_targets.extend(generator.load_aavso_targets())

    if add_manual:
        star_names = collect_manual_stars()
        if star_names:
            print(f'\nLooking up {len(star_names)} star(s) in VSX...')
            for name in star_names:
                target = generator.build_manual_target(name)
                if target is not None:
                    # Avoid duplicates if the star is also in the API list
                    already = any(t['star_name'].lower() == target['star_name'].lower()
                                  for t in all_targets)
                    if already:
                        logging.info(f'"{target["star_name"]}" already in target list — upgrading to manual/priority')
                        for t in all_targets:
                            if t['star_name'].lower() == target['star_name'].lower():
                                t['_manual'] = True
                                t['priority'] = True
                    else:
                        all_targets.append(target)

    if not all_targets:
        print('No targets found. Exiting.')
        return

    print(f'\nTotal targets to consider: {len(all_targets)}')
    print('Checking observability for tonight...\n')

    observable = generator.get_observable_stars(all_targets)

    if not observable:
        print('\nNo observable targets tonight.')
        return

    print(f'\nObservable tonight: {len(observable)} target(s)')
    for name in observable:
        print(f'  • {name}')

    if not prompt_yes_no('\nGenerate EKOS schedule file?', default=True):
        print('Schedule generation cancelled.')
        return

    generator.build_ekos_schedule(all_targets, observable)
    print('\nDone.')


if __name__ == '__main__':
    main()
