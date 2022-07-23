class InstructionTrial(Trial):
    """ Simple trial with instruction text. """

    def __init__(self, session, trial_nr, phase_durations=[np.inf],
                 txt=None, keys=None, draw_each_frame=False, **kwargs):

        super().__init__(session, trial_nr, phase_durations, draw_each_frame=draw_each_frame, **kwargs)

        txt_height = self.session.settings['various'].get('text_height')
        txt_width = self.session.settings['various'].get('text_width')
        text_position_x = self.session.settings['various'].get('text_position_x')
        text_position_y = self.session.settings['various'].get('text_position_y')

        if txt is None:
            txt = '''Press any button to continue.'''

        self.text = TextStim(self.session.win, txt,
                             height=txt_height,
                             wrapWidth=txt_width,
                             pos=[text_position_x, text_position_y],
                             font='Songti SC',
                             alignText = 'center',
                             anchorHoriz = 'center',
                             anchorVert = 'center')
        self.text.setSize(txt_height)

        self.keys = keys

    def draw(self):
        self.session.fixation.draw()
        self.session.report_fixation.draw()

        self.text.draw()
        self.session.win.flip()

    def get_events(self):
        events = super().get_events()

        if self.keys is None:
            if events:
                self.stop_phase()
        else:
            for key, t in events:
                if key in self.keys:
                    self.stop_phase()


class DummyWaiterTrial(InstructionTrial):
    """ Simple trial with text (trial x) and fixation. """

    def __init__(self, session, trial_nr, phase_durations=None,
                 txt="Waiting for scanner triggers.", draw_each_frame=False, **kwargs):

        super().__init__(session, trial_nr, phase_durations, txt, draw_each_frame=draw_each_frame, **kwargs)

    def draw(self):
        self.session.fixation.draw()
        if self.phase == 0:
            self.text.draw()
        else:
            self.session.report_fixation.draw()
        self.session.win.flip()

    def get_events(self):
        events = Trial.get_events(self)

        if events:
            for key, t in events:
                if key == self.session.mri_trigger:
                    if self.phase == 0:
                        self.stop_phase()
                        self.session.win.flip()
                        #####################################################
                        ## TRIGGER HERE
                        #####################################################
                        self.session.experiment_start_time = getTime()
                        self.session.parallel_trigger(self.session.settings['design'].get('ttl_trigger_start'))


class OutroTrial(InstructionTrial):
    """ Simple trial with only fixation cross.  """

    def __init__(self, session, trial_nr, phase_durations, txt='', draw_each_frame=False, **kwargs):

        txt = ''''''
        super().__init__(session, trial_nr, phase_durations, txt=txt, draw_each_frame=draw_each_frame, **kwargs)

    def get_events(self):
        events = Trial.get_events(self)

        if events:
            for key, t in events:
                if key == 'space':
                    self.stop_phase()

class ExpOriMapperTrial(Trial):

    def __init__(self, session, trial_nr, phase_durations, phase_names,
                 parameters, timing, load_next_during_phase,
                 verbose, condition='hrf'):
        """ Initializes a ExpOriMapperTrial object.

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
            stim_index = min(total_stim_time // self.duration_per_image,
                             len(self.parameters['stim_list'])-1)
            self.session.stimuli[self.parameters['stim_list']
                                 [stim_index]].draw()
        self.session.fixation_dot.draw()
