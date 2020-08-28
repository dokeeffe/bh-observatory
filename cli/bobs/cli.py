import os, time
import posixpath
import sys

import click

'''
TODO: Option to test all devices after indi starts and connects

'''
class Operations:
    def __init__(self):
        self.config = {}
        self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            click.echo(f"  config[{key}] = {value}", file=sys.stderr)

    def __repr__(self):
        return f"<Operations {self.config}>"

    def boot(self):
        print('wakeonlan b4:b5:2f:cd:bd:05')
        time.sleep(10)

    def power(self, device, on):
        pass
        
    def indi(self, action):
        pass

    def roof(self, action):
        pass

    def status(self, system):
        return 'Online'

pass_operations = click.make_pass_decorator(Operations)


@click.group()
@click.option(
    "--config",
    nargs=2,
    multiple=True,
    metavar="KEY VALUE",
    help="Overrides a config key/value pair.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.version_option("0.1")
@click.pass_context
def cli(ctx, config, verbose):
    """Bobs is the command line tool to manage observatory operations.
    """
    # Create an Operations object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_operations decorator.
    ctx.obj = Operations()
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)

@cli.command()
@pass_operations
def boot(operations):
    """Start the main observatory PC.
    """
    click.echo(f"Starting PC")
    operations.boot()


@cli.command()
@pass_operations
def status(operations):
    """Show status of all systems.
    """
    click.echo(f"Status")
    click.echo(f" Weather       |      {operations.status('weather')} ")
    click.echo(f" Roof          |      {operations.status('roof')} ")
    click.echo(f" Main PC       |      {operations.status('pc')} ")
    click.echo(f" Heaters       |      {operations.status('heaters')} ")
    click.echo(f" Dehumidifier  |      {operations.status('dehumidifer')} ")
    click.echo(f" Focuser       |      {operations.status('focuser')} ")
    click.echo(f" Mount         |      {operations.status('mount')} ")
    click.echo(f" CCD           |      {operations.status('ccd')} ")

@cli.command()
@click.option('--all', 'device', flag_value=['ccd','mount', 'focuser', 'heaters'],
              default=True, help="All devices except weather device")
@click.option('--ccd', 'device', flag_value=['ccd'])
@click.option('--mount', 'device', flag_value=['mount'])
@click.option('--focuser', 'device', flag_value=['focuser'])
@click.option('--weather', 'device', flag_value=['weather'])
@click.option('--heaters', 'device', flag_value=['heaters'])
@pass_operations
def poweroff(operations, device):
    """Power off a device.
    This will power off a device with no prior safety check.
    """
    operations.power(device, False)
    click.echo(f"{device} OFF")

@cli.command()
@click.option('--all', 'device', flag_value=['ccd','mount', 'focuser', 'heaters'],
              default=True, help="All devices except weather device")
@click.option('--ccd', 'device', flag_value=['ccd'])
@click.option('--mount', 'device', flag_value=['mount'])
@click.option('--focuser', 'device', flag_value=['focuser'])
@click.option('--weather', 'device', flag_value=['weather'])
@click.option('--heaters', 'device', flag_value=['heaters'])
@pass_operations
def poweron(operations, device):
    """Power on a device.
    This will power on a device.
    """
    operations.power(device, True)
    click.echo(f"{device} ON")

@cli.command()
@click.option('--start', 'action', flag_value='start')
@click.option('--stop', 'action', flag_value='stop')
@pass_operations
def indi(operations, action):
    """Control the INDI server.
    """
    operations.indi(action)
    click.echo(f"{action} indiserver")

@cli.command()
@click.option('--open', 'action', flag_value='open')
@click.option('--close', 'action', flag_value='close')
@pass_operations
def roof(operations, action):
    """Control the roof. Safety checks are performed before movement.
    """
    operations.roof(action)
    click.echo(f"Roof {action}")

@cli.command()
@click.option('--start', 'action', flag_value='start')
@click.option('--stop', 'action', flag_value='stop')
@click.option('-f', '--schedule-file')
@pass_operations
def scheduler(operations, action, schedule_file):
    """Control the indi scheduler
    """
    click.echo(f'Scheduler action {action} file {schedule_file}')