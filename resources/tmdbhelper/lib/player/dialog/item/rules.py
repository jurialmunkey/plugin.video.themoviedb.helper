from jurialmunkey.ftools import cached_property


class PlayerItemAssertRule:
    def __init__(self, item, rule):
        self.item = item  # Item details
        self.rule = rule  # Player assert rules

    @cached_property
    def inverted(self):
        return self.rule.startswith('!')

    @cached_property
    def key(self):
        return self.rule[1:] if self.inverted else self.rule

    @cached_property
    def value(self):
        return self.item.get(self.key)

    @cached_property
    def condition(self):
        return bool(self.value and self.value != 'None')

    @cached_property
    def is_valid(self):
        return bool(not self.condition) if self.inverted else self.condition
