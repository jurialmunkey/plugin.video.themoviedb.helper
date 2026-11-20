import random


class ImageArtworkCycle:
    """ Shuffled cycle through artwork slots that reads each drawn slot and skips blank or already shown images """

    def __init__(self, get_slots):
        self.get_slots = get_slots
        self.reset()

    def reset(self):
        self.cycle = self.get_cycle()
        self.used = set()
        self.is_fresh = True

    def get_cycle(self):
        slots = list(self.get_slots())
        random.shuffle(slots)
        return (slot for slot in slots)

    def is_usable(self, image):
        return bool(image) and image not in self.used

    def get_pass(self, resolve):
        """ Next usable image remaining in this pass or None once the pass is exhausted """
        self.is_fresh = False
        return next(
            (
                image
                for image in (resolve(slot) for slot in self.cycle)
                if self.is_usable(image)
            ),
            None,
        )

    def get_rebuilt_pass(self, resolve):
        self.reset()
        return self.get_pass(resolve)

    def get_next(self, resolve):
        """ Rebuild once when exhausted unless this pass was only just built so blank items aren't read twice """
        is_fresh = self.is_fresh
        image = self.get_pass(resolve) or (None if is_fresh else self.get_rebuilt_pass(resolve))
        self.used.add(image)
        return image


class ImageArtworkCycles:
    """ Artwork cycles kept while staying on an item with one draw per cycle each refresh shared by all image manipulations """

    def __init__(self):
        self.reset()

    def reset(self):
        self.cycles = {}
        self.advance()

    def advance(self):
        self.picks = {}

    def get_cycle(self, key, get_slots):
        try:
            return self.cycles[key]
        except KeyError:
            self.cycles[key] = ImageArtworkCycle(get_slots)
            return self.cycles[key]

    def get_artwork(self, key, get_slots, resolve):
        try:
            return self.picks[key]
        except KeyError:
            self.picks[key] = self.get_cycle(key, get_slots).get_next(resolve)
            return self.picks[key]
