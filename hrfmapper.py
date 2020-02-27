from exptools2.core import Session
import numpy as np
import h5py
from psychopy.visual import GratingStim, Circle

class HRFMapperSession(Session):
    def create_trials(self):
        """ Creates trials before running the session"""
        exp_s = self.settings['experiment']

        # get stimuli
        with h5py.File(exp_s['stim_file'], 'r') as f:
            self.stim_rgb_arr = np.array(f['patterns'])
        self.stimuli = [GratingStim(win=self.session.win, tex=s.T) for s in self.stim_rgb_arr]
        self.fixation_dot = Circle(self.win, radius=0.1, edges=100, color='r')

        # timings that define how many trials etc.
        mean_trial_duration = exp_s['isi_min'] + exp_s['isi_mean']
        self.n_trials = round((exp_s['total_run_duration'] - (exp_s['start_end_period'] * 2)) / mean_trial_duration)
        tolerance_range = [exp_s['total_run_duration'] - exp_s['temporal_tolerance'], exp_s['total_run_duration'] + exp_s['temporal_tolerance']]

        # and then search for the right isis to fill up the experiment exactly.
        isis = np.random.exponential(exp_s['isi_mean'], n_trials) + exp_s['isi_min']
        exp_duration = isis + (exp_s['start_end_period'] * 2)
        while exp_duration < tolerance_range[0] or exp_duration > tolerance_range[1]:
            isis = np.random.exponential(exp_s['isi_mean'], n_trials) + exp_s['isi_min']
            exp_duration = isis + (exp_s['start_end_period'] * 2)

        # deciding which stimuli to show when
        self.how_many_images_per_trial = exp_s['stim_flicker_freq'] * exp_s['stim_duration']
        self.duration_per_image = 1.0/exp_s['stim_flicker_freq']

        trial_images = np.random.randint(len(self.stimuli), size=(self.n_trials, self.how_many_images_per_trial))

        for i in range(self.n_trials):
            self.trials.append(HRFMapperTrial(
                    session=self,
                    trial_nr=i,
                    phase_durations=[0.0, exp_s['stim_duration'], isis[i]-exp_s['stim_duration']],
                    phase_names=['slack', 'stim', 'isi'],
                    parameters={'isi': isis[i],
                                'stim_list': trial_images[i]},
                    timing='seconds',
                    load_next_during_phase=None,
                    verbose=True,
                    condition='hrf'
            ))

    def run(self):
        """ Loops over trials and runs them! """

        self.create_trials()  # create them *before* running!
        self.start_experiment()

        for trail in self.trials:
            trial.run()

        self.close()


class HRFMapperTrial(Trial):

    def __init__(self, session, trial_nr, phase_durations, phase_names,
                 parameters, timing, load_next_during_phase,
                 verbose, condition='hrf'):
        """ Initializes a HRFMapperTrial object.

        Parameters
        ----------
        session : exptools Session object
            A Session object (needed for metadata)
        trial_nr: int
            Trial nr of trial
        phase_durations : array-like
            List/tuple/array with phase durations
        phase_names : array-like
            List/tuple/array with names for phases (only for logging),
            optional (if None, all are named 'stim')
        parameters : dict
            Dict of parameters that needs to be added to the log of this trial
        timing : str
            The "units" of the phase durations. Default is 'seconds', where we
            assume the phase-durations are in seconds. The other option is
            'frames', where the phase-"duration" refers to the number of frames.
        load_next_during_phase : int (or None)
            If not None, the next trial will be loaded during this phase
        verbose : bool
            Whether to print extra output (mostly timing info)
        condition : str
            Condition of the Stroop trial (either 'congruent' or 'incongruent')
        """
        super().__init__(session, trial_nr, phase_durations, phase_names,
                         parameters, timing, verbose, load_next_during_phase)
        self.condition = condition
        self.last_fix_time, self.last_stim_time = 0.0

    def draw(self):
        if self.phase == 0:  # Python starts counting from 0, and so should you
            self.last_fix_time = self.session.clock.getTime()
        elif self.phase == 1:  # assuming that there are only 2 phases
            self.last_stim_time = self.session.clock.getTime()
            total_stim_time = self.last_stim_time - self.last_fix_time
            stim_index = min(total_stim_time // self.duration_per_image, len(self.parameters['stim_list']-1)
            self.session.stimuli[self.parameters['stim_list'][stim_index]].draw()
        self.fixation_dot.draw()


