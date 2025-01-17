from readchar import key

from inquirer import errors
from inquirer.render.console.base import MAX_OPTIONS_DISPLAYED_AT_ONCE
from inquirer.render.console.base import BaseConsoleRender
from inquirer.render.console.base import half_options


class Checkbox(BaseConsoleRender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection = [k for (k, v) in enumerate(self.question.choices) if v in (self.question.default or [])]
        self.current = 0

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= MAX_OPTIONS_DISPLAYED_AT_ONCE

    def get_options(self):
        choices = self.question.choices or []
        if self.is_long:
            cmin = 0
            cmax = MAX_OPTIONS_DISPLAYED_AT_ONCE

            if half_options < self.current < len(choices) - half_options:
                cmin += self.current - half_options
                cmax += self.current - half_options
            elif self.current >= len(choices) - half_options:
                cmin += len(choices) - MAX_OPTIONS_DISPLAYED_AT_ONCE
                cmax += len(choices)

            cchoices = choices[cmin:cmax]
        else:
            cchoices = choices

        ending_milestone = max(len(choices) - half_options, half_options + 1)
        is_in_beginning = self.current <= half_options
        is_in_middle = half_options < self.current < ending_milestone
        is_in_end = self.current >= ending_milestone

        for index, choice in enumerate(cchoices):
            if (
                (is_in_middle and self.current - half_options + index in self.selection)
                or (is_in_beginning and index in self.selection)
                or (is_in_end and index + max(len(choices) - MAX_OPTIONS_DISPLAYED_AT_ONCE, 0) in self.selection)
            ):  # noqa

                symbol = self.theme.Checkbox.selected_icon
                color = self.theme.Checkbox.selected_color
            else:
                symbol = self.theme.Checkbox.unselected_icon
                color = self.theme.Checkbox.unselected_color

            selector = " "
            end_index = ending_milestone + index - half_options - 1
            if (
                (is_in_middle and index == half_options)
                or (is_in_beginning and index == self.current)
                or (is_in_end and end_index == self.current)
            ):

                selector = self.theme.Checkbox.selection_icon
                color = self.theme.Checkbox.selection_color
            yield choice, selector + " " + symbol, color

    def process_input(self, pressed):
        # Remove after merge #83
        key.SHIFT_TAB = "\x1b\x5b\x5a"
        question = self.question
        if pressed in (key.UP, key.SHIFT_TAB):
            if question.carousel and self.current == 0:
                self.current = len(question.choices) - 1
            else:
                self.current = max(0, self.current - 1)
            return
        elif pressed in (key.DOWN, key.CTRL_I):
            if question.carousel and self.current == len(question.choices) - 1:
                self.current = 0
            else:
                self.current = min(len(self.question.choices) - 1, self.current + 1)
            return
        elif pressed == key.SPACE:
            if self.current in self.selection:
                self.selection.remove(self.current)
            else:
                self.selection.append(self.current)
        elif pressed == key.LEFT:
            if self.current in self.selection:
                self.selection.remove(self.current)
        elif pressed == key.RIGHT:
            if self.current not in self.selection:
                self.selection.append(self.current)
        elif pressed == key.CTRL_A:
            for x in self.question.choices:
                self.selection = list(range(len(self.question.choices)))
        elif pressed == key.CTRL_Q:
            self.selection = []
        elif pressed == key.ENTER:
            result = []
            for x in self.selection:
                value = self.question.choices[x]
                result.append(getattr(value, "value", value))
            raise errors.EndOfInput(result)
        elif pressed == key.CTRL_C:
            raise KeyboardInterrupt()
