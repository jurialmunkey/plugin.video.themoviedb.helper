import re
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.plugin import KeyGetter


class RuleItemStepEvaluator:

    def __init__(self, item, rule_key, rule_val):
        self.item = item
        self.rule_key = rule_key
        self.rule_val = self.item.main.mapper(rule_val)

    @cached_property
    def item_val(self):
        return f'{self.item.meta_get(self.rule_key) or ""}'  # Wrangle to string

    @cached_property
    def is_position(self):
        return bool(try_int(self.rule_val) == self.item.indx + 1)

    @cached_property
    def is_valid(self):
        if self.rule_key == 'position':
            return self.is_position
        if not self.item_val:
            return False
        if not re.match(self.rule_val, self.item_val):
            return False
        return True


class RuleItemEvaluator:

    def __init__(self, main, indx, meta):
        self.main = main
        self.indx = indx
        self.meta = meta

    @cached_property
    def meta_getter(self):
        return KeyGetter(self.meta)

    def meta_get(self, key):
        return self.meta_getter.get_key(key)

    @cached_property
    def file(self):
        return self.meta_get('file')

    @cached_property
    def name(self):
        return self.meta_get('label')

    @cached_property
    def filetype(self):
        return self.meta_get('filetype')

    @cached_property
    def is_folder(self):
        return bool(self.filetype != 'file')

    @cached_property
    def item_tuple(self):
        return (self.file, self.is_folder)

    @property
    def rule_item_generator(self):
        return (
            RuleItemStepEvaluator(self, rule_key, rule_val)
            for rule_key, rule_val in self.main.action.items()
        )

    @cached_property
    def is_valid(self):
        if not self.file:
            return False
        # if not self.main.action:
        #     return False
        return all((i.is_valid for i in self.rule_item_generator))


class RuleEvaluator:

    """
    Evaluate a json_rpc directory of fileitems against a dictionary of action rules
    Strict only finds first exact match else return a list of possible matches
    """

    def __init__(self, mapper, folder, action, strict=False, dialog=False):
        self.mapper = mapper
        self.folder = folder
        self.action = action
        self.strict = strict
        self.dialog = dialog

    @property
    def rule_item_generator(self):
        return (i for i in (
            RuleItemEvaluator(self, indx, meta)
            for indx, meta in enumerate(self.folder)
        ) if i.is_valid)

    @cached_property
    def first_match(self):
        return next(self.rule_item_generator, None)

    @cached_property
    def all_matches(self):
        return list(self.rule_item_generator)

    def dialog_select(self, folder):
        from tmdbhelper.lib.player.actions.dialog import PlayerActionDialog
        return PlayerActionDialog(folder).item_tuple

    OUTPUT_EMPTY = 0
    OUTPUT_FIRST = 1
    OUTPUT_ITEMS = 2

    @cached_property
    def is_dialog_auto(self):
        return bool(self.dialog and self.dialog.lower() == 'auto')

    @cached_property
    def is_dialog_true(self):
        return bool(self.dialog and self.dialog.lower() == 'true')

    @cached_property
    def output_type(self):
        if not self.first_match:
            return self.OUTPUT_EMPTY

        if self.is_dialog_true:
            return self.OUTPUT_ITEMS

        if len(self.all_matches) == 1:
            return self.OUTPUT_FIRST

        if self.is_dialog_auto:
            return self.OUTPUT_ITEMS

        if self.strict:
            return self.OUTPUT_EMPTY

        return self.OUTPUT_FIRST

    @cached_property
    def output(self):
        """
        Returns None if no matches are found
        Returns tuple pair of file and is_folder of first match if not strict or only one match found
        Returns list of file meta of all matches if strict and more than one match found
        """

        routes = {
            self.OUTPUT_EMPTY: lambda: None,
            self.OUTPUT_FIRST: lambda: self.first_match.item_tuple,
            self.OUTPUT_ITEMS: lambda: self.dialog_select([i.meta for i in self.all_matches]),
        }

        return routes[self.output_type]()

    @property
    def file_path(self):
        try:
            return self.output[0]
        except TypeError:
            return

    @property
    def is_folder(self):
        try:
            return self.output[1]
        except TypeError:
            return
