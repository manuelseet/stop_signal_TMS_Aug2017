# -*- coding: utf-8 -*-
import codecs
import os
import string
import tempfile
import textwrap

from psychopy import core, gui, parallel, visual


class InstructionDisplay(object):

    def __init__(self,
                 window,
                 keyboard,
                 instruction_filenames,
                 continue_key=' ',
                 back_key='backspace'):
        self.window = window
        self.keyboard = keyboard
        self.instruction_filenames = instruction_filenames
        self.continue_key = continue_key
        self.back_key = back_key
        self.instruction_texts = self._read_text_files()
        self.screens = self._create_stims()
        self.current_screen_num = 0

    @staticmethod
    def _center_text(text):
        max_width = max(len(line) for line in text.splitlines())
        centered_text = ''
        for line in text.splitlines():
            # Left-justifying seems to give the best results when
            #   trying to display multiple lines of text
            centered_line = line.ljust(max_width)
            centered_text += centered_line + '\n'
        return centered_text

    def _read_text_files(self):
        texts = []
        for screen_num, filename in enumerate(self.instruction_filenames):
            # Need to use unicode as it's sometimes useful to include
            #   symbols (e.g. ←) in an instruction screen
            with codecs.open(filename, encoding='utf-8') as file_in:
                text_str = file_in.read()
                centered = self._center_text(text_str)

            texts.append(centered)

        return texts

    def _create_stims(self):
        stims = []

        for screen_num, text in enumerate(self.instruction_texts):
            stim = visual.TextStim(
                self.window,
                text=text,
                height=24,
                color='black',
                units='pix',
                # Set wrapWidth really high so we can just ignore it
                wrapWidth=1920
            )
            stims.append(stim)

        return stims

    def _show_screen(self, screen_num):
        stim = self.screens[screen_num]
        stim.draw()
        self.window.flip()

    def show_instructions(self):
        while self.current_screen_num < len(self.screens):
            self._show_screen(self.current_screen_num)
            pressed = self.keyboard.waitForPresses( keys=[self.continue_key, self.back_key])
            for event in pressed:
                key = event.key
                if key == self.continue_key:
                    self.current_screen_num += 1
                elif key == self.back_key:
                    if self.current_screen_num > 0:
                        self.current_screen_num -= 1

        self.window.flip()


def show_single_instruction_screen(filename, window, keyboard,
                                   continue_key=' '):
    # Need to use unicode as it's sometimes useful to include
    #   symbols (e.g. ←) in an instruction screen
    with codecs.open(filename, encoding='utf-8') as file_in:
        text_str = file_in.read()

    max_width = max(len(line) for line in text_str.splitlines())

    centered_text = ''
    for line in text_str.splitlines():
        # Left-justifying seems to give the best results when
        #   trying to display multiple lines of text
        centered_line = line.ljust(max_width)
        centered_text += centered_line + '\n'

    text = visual.TextStim(
        window,
        text=centered_text,
        height=24,
        color='black',
        units='pix',
        # Set wrapWidth really high so we can just ignore it
        wrapWidth=1920
    )
    text.draw()
    window.flip()
    keyboard.waitForPresses(keys=[continue_key])
    window.flip()


class ParallelController(object):

    def __init__(self, port_address=0xd050):
        self.port = parallel.ParallelPort(port_address)

    def fire_at_deadline(self, time_to_fire):
        self.port.setData(10)
        core.wait(time_to_fire)
        self.port.setData(0)


def get_subject_info():
    """
    Show a GUI dialog with a few different fields to fill in and
    return the results as a dict (or exit the experiment if the
    cancel button is clicked.

    Most of this can be done using PsychoPy's gui.DlgFromDict, but
    doing it this way, we can:
        * Have labels for each field that are different to the key in
          the returned dictionary ('subject_id' in the dictionary and
          a more readable 'Subject ID:' as the field label)
        * Convert values automatically, e.g. convert age to an int
    """
    fields = [
        ('subject_id', {'label': 'Subject ID:'}),
        ('condition', {'label': 'Condition:', 'choices': ['1', '2']}),
        ('session_type', {
            'label': 'Training or Test:',
            'choices': [
                'Training',
                'Test'
            ]
        }),
        ('age', {'label': 'Age:'}),
        ('sex', {'label': 'Sex', 'choices': ['Female', 'Male']}),
        ('handed', {'label': 'Handed', 'choices': ['Right', 'Left']}),
        ('stimulation_intensity', {'label': 'Stimulation Intensity', 'initial': 0})
    ]
    # Most fields are OK to leave as string, otherwise convert
    conversions = {
        'age': int,
        'stimulation_intensity': int
    }
    info_dialog = gui.Dlg(title='Enter subject information:')
    for field_name, args in fields:
        info_dialog.addField(**args)
    info_dialog.show()
    if not info_dialog.OK:
        raise KeyboardInterrupt("User cancelled, exiting.")
    # Store the results under the original fieldnames
    final_results = {fields[i][0]: info_dialog.data[i]
                     for i in range(len(fields))}
    # Convert data types for fields listed in conversions dict
    for key, convert_func in conversions.items():
        final_results[key] = convert_func(final_results[key])
    return final_results


def check_if_file_exists(filename):
    if os.path.exists(filename):
        raise ValueError(
            "Filename: {}\n"
            "  already exists! Choose a different subject ID"
            "  or delete the existing files".format(filename)
        )


def check_refresh_rate(window, desired_rate):
    actual_refresh_rate = window.getActualFrameRate()
    if not desired_rate == round(actual_refresh_rate):
        error_text = ("Measured refresh rate {a} not equal to desired"
                      " frame rate {s}")
        raise ValueError(error_text .format(
                a=actual_refresh_rate,
                s=desired_rate
        ))
    else:
        print(
            ("Screen refresh rate looks OK:\n"
             "    Measured: {a} Hz\n"
             "    Desired: {s} Hz").format(
                a=actual_refresh_rate,
                s=desired_rate
            ))


def save_psychopy_data_workaround(filename, trial_handler, append=False):
    """
    Currently to get a nice CSV out of PsychoPy you have to use
    TrialHandler.saveAsWideText() first, and then use the
    DataFrame you get out of that to save a proper CSV.

    This dumps the badly formatted file you get out of TrialHandler
    to a temporary file and only saves the proper CSV.
    """
    temp = tempfile.NamedTemporaryFile(mode='w')
    data_as_df = trial_handler.saveAsWideText(temp.name)
    # TODO: Hopefully change this once I land the PR and PsychoPy
    #   starts raising an exception here
    # If we exit the experiment early and there's no actual
    #   data in the trial_handler, saveAsWideText() returns
    #   -1 instead of a DataFrame
    if type(data_as_df) == int:
        print("No data in trial handler, nothing to save.")
        return
    if append:
        data_as_df.to_csv(
            filename,
            index=False,
            header=False,
            mode='a',
            line_terminator='\n'
        )
    else:
        data_as_df.to_csv(
            filename,
            index=False,
            header=True,
            mode='w',
            line_terminator='\n'
        )


def do_vowel_count_question(correct_n, window, keyboard):
    question_text = textwrap.dedent("""
    How many vowels did you count in the last block?
    Type the number and press ENTER.
    You can press Backspace to fix your mistakes.

    {answer:^60}""")
    current_answer = ''

    stim = visual.TextStim(
        window,
        text=question_text.format(answer=current_answer),
        height=24,
        color='black',
        units='pix',
        wrapWidth=1920
    )
    stim.draw()
    window.flip()

    waiting_for_answer = True
    while waiting_for_answer:
        waiting_for_key = True
        while waiting_for_key:
            key_presses = keyboard.getPresses()
            for event in key_presses:
                waiting_for_key = False
                if event.key in ('num_enter', 'return'):
                    # Only finish if participant enters a valid
                    # int
                    try:
                        entered_answer = int(current_answer.strip())
                        waiting_for_answer = False
                    except ValueError:
                        pass
                elif event.key == 'backspace':
                    current_answer = current_answer[:-1]
                # Checking event.char allows for both the numpad and the
                #   top row of numbers to register properly
                elif event.char in string.digits:
                    current_answer += event.char
            core.wait(0.005)

        new_text = question_text.format(answer=current_answer)
        # Setting stim.text like this is very slow, don't do it
        #   in a timing-based part of the experiment. For questions
        #    screens like this it's OK
        stim.text = new_text
        stim.draw()
        window.flip()

    count_is_correct = entered_answer == correct_n

    if count_is_correct:
        stim.text = InstructionDisplay._center_text(
            "Correct!\n\nPress ENTER to continue with the next block"
        )
    else:
        feedback_template = (
            "Incorrect\n\nYour answer: {entered}\n\n"
            "Actual count: {actual}\n\n"
            "Press ENTER to continue with the next block"
        )
        stim.text = InstructionDisplay._center_text(
            feedback_template.format(
                entered=entered_answer,
                actual=correct_n
            )
        )
    stim.draw()
    window.flip()
    keyboard.waitForPresses(keys=['num_enter', 'return'])

    return entered_answer, count_is_correct

if __name__ == '__main__':
    window = visual.Window(
        size=(800, 600),
        fullscr=False,
        winType='pyglet',
        units='pix'
    )
    example_screens = [
        'Instructions/example_instructions_1.txt',
        'Instructions/example_instructions_2.txt',
        'Instructions/example_instructions_3.txt'
    ]
    instructions = InstructionDisplay(
        window,
        instruction_filenames=example_screens
    )
    instructions.show_instructions()
