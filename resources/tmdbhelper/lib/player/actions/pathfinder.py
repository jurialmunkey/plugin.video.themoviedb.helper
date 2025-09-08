from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import get_directory
from tmdbhelper.lib.addon.plugin import KeyGetter


class PathFinderAction:

    keyboard_directions = ('Up', 'Down', 'Left', 'Right', 'Select')

    def __init__(self, parent, action):
        self.parent = parent
        self.action = action
        self.bypass = action.pop('return', None)
        self.dialog = action.pop('dialog', None)
        self.strict = action.pop('strict', None)

    """
    action
    """

    @cached_property
    def action_getter(self):
        return KeyGetter(self.action)

    def action_get(self, key):
        return self.action_getter.get_key(key)

    """
    Keyboard inputter
    """

    @cached_property
    def keyboard(self):
        return self.action_get('keyboard')

    @cached_property
    def keyboard_rtl(self):
        return bool(self.action_get('direction') == 'rtl')

    @cached_property
    def keyboard_text(self):
        keyboard_text = self.parent.mapper(self.keyboard)
        keyboard_text = keyboard_text[::-1] if self.keyboard_rtl else keyboard_text
        return keyboard_text

    @cached_property
    def keyboard_inputter(self):
        from tmdbhelper.lib.player.inputter import KeyboardInputter
        if self.keyboard in self.keyboard_directions:
            return KeyboardInputter(action=f'Input.{self.keyboard}')
        return KeyboardInputter(text=self.keyboard_text)

    @cached_property
    def keyboard_initialised(self):
        if not self.keyboard:
            return False
        self.parent.keyboard_inputter = self.keyboard_inputter
        self.parent.keyboard_inputter.setName('keyboard_input')
        self.parent.keyboard_inputter.start()
        return True

    """
    Rule Evaluator
    """

    @cached_property
    def rule_evaluator(self):
        from tmdbhelper.lib.player.actions.evaluator import RuleEvaluator
        return RuleEvaluator(self.parent.mapper, self.folder, self.action, self.strict, self.dialog)

    @property
    def file_path(self):
        return self.rule_evaluator.file_path

    @property
    def is_folder(self):
        return self.rule_evaluator.is_folder

    @cached_property
    def folder(self):
        folder = get_directory(self.parent.mapper(self.parent.file_path))
        self.parent.keyboard_inputter_exit()  # Stop keyboard from previous step once directory retrieved
        return folder

    @cached_property
    def status(self):

        if self.keyboard_initialised:
            return self.parent.STATUS_NEXT

        if not self.file_path:
            return self.parent.STATUS_FAIL

        self.parent.file_path = self.file_path
        self.parent.is_folder = self.is_folder

        if not self.is_folder and self.bypass:
            return self.parent.STATUS_DONE

        if self.is_folder and self.dialog == 'repeat':
            path_finder_action = PathFinderAction(self.parent, {})
            path_finder_action.bypass = self.bypass
            path_finder_action.dialog = self.dialog
            path_finder_action.strict = self.strict
            return path_finder_action.status

        return self.parent.STATUS_NEXT


class PathFinder:

    def __init__(self, mapper, action, is_folder=True):
        self.mapper = mapper
        self.action = action
        self.is_folder = is_folder
        self.keyboard_inputter = None

    def keyboard_inputter_exit(self):
        try:
            self.keyboard_inputter.exit = True
            self.keyboard_inputter = None
        except AttributeError:
            return

    @cached_property
    def file_path(self):
        return self.action[0]

    @property
    def action_generator(self):
        return (i.status for i in (
            PathFinderAction(self, action)
            for action in self.action[1:]
        ) if i.status)

    STATUS_NEXT = 0
    STATUS_DONE = 1
    STATUS_FAIL = 2

    @cached_property
    def status(self):
        return next(self.action_generator, self.STATUS_DONE)

    @cached_property
    def path_tuple(self):
        if not self.is_folder:
            return (self.file_path, self.is_folder)
        if self.status == self.STATUS_DONE:
            return (self.file_path, self.is_folder)
