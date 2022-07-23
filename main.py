import click
from .exporimapper import ExpOriMapperSession


@click.command()
@click.option('--sub', default='01', type=str, help='Subject nr (e.g., 01)')
@click.option('--run', default=1, type=int, help='Run nr')
@click.option('--settings', default='defaults.yml', type=str, help='Settings file')
@click.option('--task', default='train', type=str, help='Type of run (train, test)')

def main_api(sub, run, dummies, settings):

    eomapper_session = ExpOriMapperSession(
        sub=sub,
        run=run,
        output_str=f'sub-{sub}_task-hrf_run-{run}',
        settings_file=settings
    )

    eomapper_session.run()
    eomapper_session.quit()
