import necrobot.exception
from necrobot.util.necrodancer import seedgen
from necrobot.util.category import Category


class RaceInfo(object):
    @staticmethod
    def copy(race_info):
        the_copy = RaceInfo()

        the_copy.seed = seedgen.get_new_seed()

        the_copy.category = race_info.category
        the_copy.cat_str = race_info.cat_str
        the_copy.seeded = race_info.seeded
        the_copy.can_be_solo = race_info.can_be_solo
        the_copy.post_results = race_info.post_results
        the_copy.condor_race = race_info.condor_race
        the_copy.private_race = race_info.private_race

        return the_copy

    def __init__(self, category=Category.ASO, cat_str=None, seeded=False):
        self.category = category
        self.cat_str = str(self.category) if cat_str is None else cat_str
        self.seeded = seeded

        self.seed = 0
        self.can_be_solo = False
        self.post_results = True
        self.condor_race = False
        self.private_race = False

    # a string "Seed: (int)" if the race is seeded, or the empty string otherwise
    @property
    def seed_str(self):
        if self.seeded:
            return 'Seed: {0}'.format(self.seed)
        else:
            return ''


def parse_args(args):
    seeded = '-s' in args or '--seeded' in args

    for arg in args.copy():
        if arg.startswith('-'):
            args.remove(arg)

    if not args:
        return RaceInfo(seeded=seeded)
    elif args[0].lower() == 'custom':
        try:
            return RaceInfo(Category.CUSTOM, args[1], seeded)
        except IndexError:
            raise necrobot.exception.ParseException('Provide a description. Ex: `.make custom "Max Low"`')
    else:
        return RaceInfo(Category.fromstr(args[0]), seeded=seeded)
