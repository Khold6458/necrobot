import necrobot.exception
from necrobot.race import raceinfo

from necrobot.race.raceinfo import RaceInfo


class MatchInfo(object):
    @staticmethod
    def copy(match_info):
        the_copy = MatchInfo()
        the_copy.max_races = match_info.max_races
        the_copy.is_best_of = match_info.is_best_of
        the_copy.ranked = match_info.ranked
        the_copy.race_info = RaceInfo.copy(match_info.race_info)
        return the_copy

    def __init__(
            self,
            max_races: int = None,
            is_best_of: bool = None,
            ranked: bool = None,
            race_info: RaceInfo = None
    ):
        self.max_races = max_races if max_races is not None else 3
        self.is_best_of = is_best_of if is_best_of is not None else False
        self.ranked = ranked if ranked is not None else False
        self.race_info = race_info if race_info is not None else RaceInfo()

    @property
    def format_str(self) -> str:
        """Get a string describing the match format."""
        if self.is_best_of:
            match_format_info = 'best-of-{0}'.format(self.max_races)
        else:
            match_format_info = '{0} races'.format(self.max_races)

        ranked_str = 'ranked' if self.ranked else 'unranked'

        return '{0}, {1}, {2}'.format(self.race_info.cat_str, match_format_info, ranked_str)


def parse_args(args: list) -> MatchInfo:
    """Parses the given command-line args into a MatchInfo."""
    seeded = '-s' in args or '--seeded' in args
    repeat = '-r' in args or '--repeat' in args

    for arg in args.copy():
        if arg.startswith('-'):
            args.remove(arg)

    if len(args) < 2:
        raise necrobot.exception.ParseException(f'Incorrect number of arguments.')

    try:
        num = int(args[1])
        del args[1]
    except ValueError:
        raise necrobot.exception.ParseException(f'Error parsing `{args[1]}` as a number of races.')

    race_info = raceinfo.parse_args(args)
    race_info.seeded = seeded

    return MatchInfo(max_races=num, is_best_of=(repeat is None), race_info=race_info)

