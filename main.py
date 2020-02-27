import click
import os.path as op
from .hrfmapper import HRFMapperSession


@click.command()
@click.option('--sub', default='01', type=str, help='Subject nr (e.g., 01)')
@click.option('--run', default=1, type=int, help='Run nr')
@click.option('--dummies', default=0, type=int, help='Number of dummy scans')
@click.option('--settings', default='settings.yml', type=str, help='Settings file')

def main_api(sub, run, dummies, settings):

    hrfmapper_session = HRFMapperSession(
        sub=sub,
        run=run,
        output_str=f'sub-{sub}_task-hrf_run-{run}',
        settings_file=settings,
        stim_dir=stimdir,
        scrambled=scrambled,
        dummies=dummies,
        ntrials=ntrials
    )

    hrfmapper_session.run()
    hrfmapper_session.quit()
