import re
from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int


class PlayerActionValidationStep:
    def __init__(self, player_action_validation, action_key, action_val):
        self.player_action_validation = player_action_validation
        self.action_key = action_key  # action key
        self.action_val = action_val  # action value formatted

    @cached_property
    def infolabel(self):
        return f'{self.player_action_validation.item.get(self.action_key, "")}'  # Wrangle to string

    @cached_property
    def is_valid(self):
        # Special keywork position to check for position instead of infolabel
        if self.key == 'position':
            return bool(try_int(self.action_val) == self.player_action_validation.posx + 1)

        # Item doesnt have that infolabel
        if not self.infolabel:
            return False

        # Regex check value against infolabel
        if not re.match(self.action_val, self.infolabel):
            return False

        return True


class PlayerActionValidation:
    def __init__(self, player_action, posx, item):
        self.player_action = player_action
        self.posx = posx
        self.item = item

    @property
    def is_valid(self):
        if not self.item.get('file'):
            return False

        for key, val in self.player_action.action.items():
            if not PlayerActionValidationStep(
                player_action_validation=self,
                action_key=key,
                action_val=self.player_action.string_format_map(val)
            ).is_valid:
                return False

        return True
