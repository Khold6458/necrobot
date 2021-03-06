# Class holding info data for a private race.

from necrobot.race import raceinfo


class PrivateRaceInfo(object):
    @staticmethod
    def copy(private_race_info):
        the_copy = PrivateRaceInfo()
        the_copy.admin_names = list(private_race_info.admin_names)
        the_copy.racer_names = list(private_race_info.racer_names)
        the_copy.race_info = raceinfo.RaceInfo.copy(private_race_info.race_info)
        return the_copy

    def __init__(self, race_info=None):
        self.admin_names = []
        self.racer_names = []
        self.race_info = race_info
