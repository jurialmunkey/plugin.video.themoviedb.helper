from tmdbhelper.lib.files.ftools import cached_property


class PlayerActionPluginKeyboard:
    keyboard_commands = ('Up', 'Down', 'Left', 'Right', 'Select')

    def __init__(self, player_action):
        self.player_action = player_action

    @cached_property
    def keyboard(self):
        return self.player_action.action['keyboard']

    @cached_property
    def keyboard_rtl(self):
        try:
            return bool(self.player_action.action['direction'] == 'rtl')
        except KeyError:
            return False

    @cached_property
    def keyboard_kwgs(self):
        if self.keyboard in self.keyboard_commands:
            return {'action': f'Input.{self.keyboard}'}
        ktext = self.player_action.string_format_map(self.keyboard)
        ktext = ktext[::-1] if self.keyboard_rtl else ktext
        return {'text': ktext}

    def run(self):
        from tmdbhelper.lib.player.inputter import KeyboardInputter
        self.player_action.player_meta.keyboard_thread = KeyboardInputter(**self.keyboard_kwgs)
        self.player_action.player_meta.keyboard_thread.setName('keyboard_input')
        self.player_action.player_meta.keyboard_thread.start()
        self.player_action.log('KEYBRD', self.keyboard)
