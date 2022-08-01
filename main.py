import click
from exporimapper import ExpOriMapperSession


@click.command()
@click.option('--sub', default=1, type=int, help='Subject nr (e.g., 1)')
@click.option('--run_id', default=1, type=int, help='Run nr')
@click.option('--ses', default=1, type=int, help='Session nr')
@click.option('--settings', default='defaults.yml', type=str, help='Settings file')
@click.option('--task', default='train', type=str, help='Type of run (train, test)')
@click.option('--eyetracker', default=False, type=bool, help='Whether to try to connect to the eyetracker')

def main_api(sub, run_id, ses, task, settings, eyetracker):
    eomapper_session = ExpOriMapperSession(
        sub=sub,
        run_id=run_id,
        ses=ses,
        task=task,
        output_str=f'sub-{str(sub).zfill(2)}_ses-{str(ses).zfill(1)}_task-{task}_run-{str(run_id).zfill(2)}',
        settings_file=settings,
        eyetracker_on=eyetracker
    )
    eomapper_session.run()
    eomapper_session.quit()


if __name__ == '__main__':
    main_api()