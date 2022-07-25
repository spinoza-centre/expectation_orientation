import click
from .exporimapper import ExpOriMapperSession


@click.command()
@click.option('--sub', default='01', type=str, help='Subject nr (e.g., 01)')
@click.option('--run', default=1, type=int, help='Run nr')
@click.option('--ses', default=1, type=int, help='Session nr')
@click.option('--settings', default='defaults.yml', type=str, help='Settings file')
@click.option('--task', default='train', type=str, help='Type of run (train, test)')

def main_api(sub, run, settings):
    eomapper_session = ExpOriMapperSession(
        sub=sub,
        run=run,
        ses=ses,
        task=task,
        output_str=f'sub-{sub.zfill(2)}_ses-{str(ses).zfill(1)}_task-{task}_run-{str(run).zfill(2)}',
        settings_file=settings
    )

    eomapper_session.run()
    eomapper_session.quit()
