import numpy as np
from psychopy.visual import TextStim, ShapeStim
from exptools2.core import Trial

class InstructionTrial(Trial):
    """ Simple trial with instruction text. """

    def __init__(self, session, trial_nr, phase_durations=[np.inf],
                 txt=None, keys=None, draw_each_frame=False, **kwargs):

        super().__init__(session, trial_nr, phase_durations,
                         draw_each_frame=draw_each_frame, **kwargs)

        txt_height = self.session.settings['various'].get('text_height')
        txt_width = self.session.settings['various'].get('text_width')
        text_position_x = self.session.settings['various'].get(
            'text_position_x')
        text_position_y = self.session.settings['various'].get(
            'text_position_y')

        if txt is None:
            txt = '''Press any button to continue.'''

        self.text = TextStim(self.session.win, txt,
                             height=txt_height,
                             wrapWidth=txt_width,
                             pos=[text_position_x, text_position_y],
                             font='Helvetica',
                             alignText='center',
                             anchorHoriz='center',
                             anchorVert='center')
        self.text.setSize(txt_height)

        self.keys = keys

    def draw(self):
        self.session.stim_position_info.draw()
        self.session.center_fixation_dot.draw()

        self.text.draw()
        self.session.win.flip()

    def get_events(self):
        events = super().get_events(timeStamped=self.session.clock)

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

        super().__init__(session, trial_nr, phase_durations,
                         txt, draw_each_frame=draw_each_frame, **kwargs)
        self.text.setOpacity(0.25)

    def draw(self):
        self.session.surround_fixation_dot.draw()
        self.session.center_fixation_dot.draw()
        if self.phase == 0:
            self.text.draw()
        self.session.win.flip()

    def get_events(self):
        events = super().get_events(self)

        if events:
            for key, t in events:
                if key == self.session.mri_trigger:
                    if self.phase == 0:
                        self.stop_phase()
                        self.session.win.flip()


class OutroTrial(InstructionTrial):
    """ Simple trial with only fixation cross.  """

    def __init__(self, session, trial_nr, phase_durations, txt='', draw_each_frame=False, **kwargs):

        txt = ''''''
        super().__init__(session, trial_nr, phase_durations,
                         txt=txt, draw_each_frame=draw_each_frame, **kwargs)

    def get_events(self):
        events = super().get_events(self)

        if events:
            for key, t in events:
                if key == 'space':
                    self.stop_phase()

    def draw(self):
        self.session.surround_fixation_dot.draw()
        self.session.center_fixation_dot.draw()
        if self.phase == 0:
            self.text.draw()
        self.session.win.flip()


class ExpOriMapperTrial(Trial):

    def __init__(self, session, trial_nr, phase_durations, phase_names,
                 parameters, timing, load_next_during_phase,
                 verbose, condition='train'):
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
            Condition of the trial (either 'train' or 'test')
        """
        super().__init__(session, trial_nr, phase_durations, phase_names,
                         parameters, timing, verbose, load_next_during_phase)
        self.condition = condition
        self.last_fix_time, self.last_stim_time = 0.0
        self.trial_answered = False

    def draw(self):

        exp_s = self.session.settings['experiment']

        if self.phase == 1:  # warn phase, change color of fixation marker
            self.session.center_fixation_dot.setColor(self.parameters['color'])
            self.last_fix_time = self.session.clock.getTime()
        else:
            self.session.center_fixation_dot.setColor(
                exp_s['fixation_center_color'])

        if self.phase == 2:  # stimulus phase
            draw_grating = False
            stim_time = self.session.clock.getTime()
            if (self.last_fix_time - stim_time) < exp_s['stim_duration']:
                draw_grating = True
                self.parameters['stim_value_p1'] = self.parameters['correct_response_sign'] * \
                    self.parameters['staircase_value'] / 2
                self.session.grating.setOri(self.parameters['rounded_orientation_degrees'] +
                                            self.parameters['stim_value_p1'])
            if (self.last_fix_time - stim_time) > (exp_s['stim_duration'] + exp_s['test_interstim_interval']):
                draw_grating = True
                self.parameters['stim_value_p2'] = -self.parameters['correct_response_sign'] * \
                    self.parameters['staircase_value'] / 2
                self.session.grating.setOri(self.parameters['rounded_orientation_degrees'] +
                                            self.parameters['stim_value_p2'])
            if draw_grating:
                self.session.grating.draw()

        self.session.surround_fixation_dot.draw()
        self.session.center_fixation_dot.draw()

    def get_events(self):
        exp_s = self.session.settings['experiment']
        events = super().get_events(self)

        if events:
            for key, t in events:
                if key == 'space':
                    self.stop_phase()
                if key == 't':
                    if self.phase == 1:
                        self.stop_phase()
                        self.session.win.flip()
                if self.phase == 3:
                    if not self.trial_answered:
                        if key in exp_s['cw_buttons']:
                            self.parameters['response_key'] = key
                            self.parameters['response_value'] = exp_s['cw_buttons'].index(
                                key)
                            self.parameters['response_sign'] = 1
                            self.parameters['response_time'] = t
                            if self.parameters['correct_response_sign'] == 1:
                                self.parameters['response_correct'] = 1
                            else:
                                self.parameters['response_correct'] = 0
                            self.session.staircase.addResponse(
                                self.parameters['response_correct'])
                        elif key in exp_s['ccw_buttons']:
                            self.parameters['response_key'] = key
                            self.parameters['response_value'] = exp_s['ccw_buttons'].index(
                                key)
                            self.parameters['response_sign'] = -1
                            self.parameters['response_time'] = t
                            if self.parameters['correct_response_sign'] == -1:
                                self.parameters['response_correct'] = 1
                            else:
                                self.parameters['response_correct'] = 0
                            self.session.staircase.addResponse(
                                self.parameters['response_correct'])
                        self.trial_answered = True


class PositioningTrial(Trial):
    """ Simple trial with text (trial x) and fixation. """

    def __init__(self, session, trial_nr, phase_durations=(1e9,), **kwargs):
        super().__init__(session, trial_nr, phase_durations, **kwargs)

        self.keys = self.session.settings['position_experiment']['keys']
        self.current_topic = 'x_offset'

        txt_height = self.session.settings['various'].get('text_height')
        txt_width = self.session.settings['various'].get('text_width')
        text_position_x = self.session.settings['various'].get(
            'text_position_x')
        text_position_y = self.session.settings['various'].get(
            'text_position_y')

        self.info = TextStim(self.session.win, """""",
                             height=txt_height,
                             wrapWidth=txt_width,
                             pos=[text_position_x, text_position_y],
                             font='Helvetica',
                             alignText='center',
                             anchorHoriz='center',
                             anchorVert='center')
        self.text.setSize(txt_height)

        angles = np.linspace(0, 2*np.pi, 300)
        self.shape = np.array([[np.sin(a),  np.cos(a)] for a in angles])
        self.pos_stim = ShapeStim(win=self.session.win,
                                  vertices=self.shape,
                                  size=[self.session.stim_position_info['width'],
                                        self.session.stim_position_info['height']],
                                  pos=[self.session.stim_position_info['x_offset'],
                                       self.session.stim_position_info['y_offset']])

    def draw(self):
        """ Draws stimuli """

        self.pos_stim.draw()
        self.session.pos_stim.draw()
        self.session.fixation_stimulus.draw()
        self.info.draw()

    def get_events(self):
        events = super().get_events(timeStamped=self.session.clock)

        if events:
            if 'q' in [ev[0] for ev in events]:  # specific key in settings?
                self.session.close()
                self.session.quit()

        for e in events:
            if e[0] in self.keys:
                ix = self.keys.index(e[0])

                if ix == 0:
                    if self.current_topic == 'x_offset':
                        self.session.stim_position_info['x_offset'] -= 0.1
                    elif self.current_topic == 'y_offset':
                        self.session.stim_position_info['y_offset'] -= 0.1
                    elif self.current_topic == 'width':
                        self.session.stim_position_info['width'] -= 0.1
                    elif self.current_topic == 'height':
                        self.session.stim_position_info['height'] -= 0.1
                elif ix == 1:
                    if self.current_topic == 'x_offset':
                        self.session.stim_position_info['x_offset'] += 0.1
                    elif self.current_topic == 'y_offset':
                        self.session.stim_position_info['y_offset'] += 0.1
                    elif self.current_topic == 'width':
                        self.session.stim_position_info['width'] += 0.1
                    elif self.current_topic == 'height':
                        self.session.stim_position_info['height'] += 0.1
                elif ix == 2:
                    if self.current_topic == 'x_offset':
                        self.current_topic = 'y_offset'
                    elif self.current_topic == 'y_offset':
                        self.current_topic = 'width'
                    elif self.current_topic == 'width':
                        self.current_topic = 'height'
                    elif self.current_topic == 'height':
                        self.current_topic = 'x_offset'

        if self.current_topic == 'x_offset':
            self.info.text = 'x: {:0.2f}'.format(
                self.session.stim_position_info['x_offset'])
        elif self.current_topic == 'y_offset':
            self.info.text = 'y: {:0.2f}'.format(
                self.session.stim_position_info['y_offset'])
        elif self.current_topic == 'width':
            self.info.text = 'width: {:0.2f}'.format(
                self.session.stim_position_info['width'])
        elif self.current_topic == 'height':
            self.info.text = 'height: {:0.2f}'.format(
                self.session.stim_position_info['height'])

        self.session.update_stim_position()
        self.pos_stim.setPos(
            [self.session.stim_position_info['x_offset'], self.session.stim_position_info['y_offset']])
        self.pos_stim.setSize(
            [self.session.stim_position_info['width'], self.session.stim_position_info['height']])
        self.info.setPos([self.session.stim_position_info['x_offset'],
                         self.session.stim_position_info['y_offset']])
        self.info.setSize([self.session.stim_position_info['width'],
                          self.session.stim_position_info['height']])

    def stop_trial(self):
        super().stop_trial()
        self.session.save_stimulus_position_settings()
