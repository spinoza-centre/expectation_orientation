from genericpath import isfile
from exptools2.core import EyelinkSession
import numpy as np
import h5py, yaml
import os, sys, time
import pandas as pd
from psychopy.visual import GratingStim, Circle
from .trial import InstructionTrial, DummyWaiterTrial, OutroTrial, ExpOriMapperTrial, PositioningTrial
class ExpOriMapperSession(EyelinkSession):

    def __init__(self) -> None:
        super().__init__()
        self.create_stimuli()
        self.create_trials()

    def update_stimulus_position(self):
        """ Updates the stimulus position """
        self.grating.pos = (self.stim_position_info['x_offset'], self.stim_position_info['y_offset'])
        self.grating.size = (self.stim_position_info['width'], self.stim_position_info['height'])

        for dot in [self.center_fixation_dot, self.surround_fixation_dot]:
            dot.pos = (self.stim_position_info['x_offset'], self.stim_position_info['y_offset'])

    def save_stimulus_position_settings(self):
        """ Saves the stimulus position settings to a file """
        with open(self.stim_position_settings_file, 'w') as f:
            yaml.dump(self.stim_position_info, f)

    def create_stimuli(self):
        """ Creates stimuli for the session """
        exp_s = self.settings['experiment']

        self.center_fixation_dot = Circle(
            self.win, radius=exp_s['fixation_center_size'], edges=200, color='w')
        self.surround_fixation_dot = Circle(
            self.win, radius=exp_s['fixation_surround_size'], edges=200, color=0)

        if self.run_type == 'train':
            size = exp_s['train_grating_size']
            sf = exp_s['train_grating_sf']
            contrast = exp_s['train_grating_contrast']
            fringewidth = exp_s['train_grating_fringewidth']
        elif self.run_type == 'test':
            size = exp_s['test_grating_size']
            sf = exp_s['test_grating_sf']
            contrast = exp_s['test_grating_contrast']
            fringewidth = exp_s['test_grating_fringewidth']
        else:
            raise ValueError('Unknown run type: {}'.format(self.run_type))
        self.grating = GratingStim(win=self.session.win,
                                   tex='sin',
                                   size=size,
                                   sf=sf,
                                   contrast=contrast,
                                   ori=0,
                                   phase=0,
                                   mask='raisedCos',
                                   maskParams={'fringeWidth': fringewidth},
                                   texRes=1024)

    def create_trials(self):
        """ Creates trials before running the session"""
        exp_s = self.settings['experiment']

        instruction_trial = InstructionTrial(session=self,
                                             trial_nr=0,
                                             phase_durations=[np.inf],
                                             txt=self.settings['stimuli'].get('instruction_text'),
                                             keys=['space'],
                                             draw_each_frame=False)

        dummy_trial = DummyWaiterTrial(session=self,
                                       trial_nr=1,
                                       phase_durations=[
                                       np.inf, exp_s['start_end_period']],
                                       txt=self.settings['stimuli'].get('pretrigger_text'),
                                       draw_each_frame=False)

        # paths
        default_settings_path = os.path.join(op.dirname(__file__),
                                        'defaults.yml')
        tsv_path = os.path.join(op.dirname(__file__),
            f'run_designs/sub-{str(self.sub).zfill(2)}/sub-{str(self.sub).zfill(2)}_task-{str(self.task)}_run{str(self.run).zfill(2)}.tsv')

        with open(default_settings_path, 'r', encoding='utf8') as f_in:
            default_settings = yaml.safe_load(f_in)
        self.trial_df = pd.read_csv(tsv_path, sep='\t', index_col=0, na_values='NA')

        # read in or set up stimulus positioning
        self.stim_position_settings_file = f'data/sub-{str(self.sub).zfill(2)}_ses-{str(self.ses).zfill(2)}.yml'
        if os.path.isfile(self.stim_position_settings_file):
            with open(self.stim_position_settings_file, 'r', encoding='utf8') as f_in:
                self.stim_position_info = yaml.safe_load(f_in)
            self.trials = [instruction_trial, dummy_trial]
        else:
            self.stim_position_info = default_settings['stim_position_info']
            if self.stim_position_info['repositioning_required']:
                position_trial = PositioningTrial(session=self)
                self.trials = [position_trial, instruction_trial, dummy_trial]
            else:
                self.trials = [instruction_trial, dummy_trial]

        stim_pres_duration = 2*exp_s['test_stim_duration']+exp_s['test_interstim_interval']
        remainder_trial_duration = -0.1 + exp_s['total_trial_duration'] - (stim_pres_duration + exp_s['warn_duration'])

        trial_counter = len(self.trials)
        for i in range(self.n_trials):
            # add task settings to parameters of the trial
            parameters = self.trial_df.iloc[i].to_dict()


            self.trials.append(ExpOriMapperTrial(
                session=self,
                trial_nr=i,
                phase_durations=[
                    1.0,
                    exp_s['warn_duration'],
                    stim_pres_duration,
                    remainder_trial_duration
                ],
                phase_names=['fix', 'warning', 'stim', 'response'],
                parameters=parameters,
                timing='seconds',
                load_next_during_phase=None,
                verbose=True,
                condition=self.task)
                )
            trial_counter += 1

        outro_trial = OutroTrial(session=self,
                                 trial_nr=trial_counter,
                                 phase_durations=[
                                     exp_s['start_end_period']],
                                 txt='',
                                 draw_each_frame=False)

        self.trials.append(outro_trial)

    def run(self):
        """ Loops over trials and runs them! """

        self.start_experiment()

        for trial in self.trials:
            trial.run()

        self.close()
