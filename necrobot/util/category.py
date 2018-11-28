from enum import Enum
from difflib import get_close_matches
from string import capwords

import necrobot.exception


class Category(Enum):
    ANY = 'Any%'
    HELL = 'Hell%'
    LOW = 'Low%'
    NG = 'No Gold'
    EGGY = 'Eggplant%'
    LOWHELL = 'Low% Hell'
    NGH = 'No Gold Hell%'
    LOWNG = 'Low% No Gold'
    BIGMONEY = 'Big Money'
    ASO = 'All Shortcuts + Olmec'
    MAXANY = 'Max Any%'
    MAXHELL = 'Max Hell%'
    MAXLOW = 'Max Low%'
    AJE = 'All Journal Entries'
    NOTPANY = 'No TP Any%'
    CHARS = 'All Characters'
    TEMPLE = 'Temple Shortcut%'
    ACHIEVE = 'All Achievements'
    CUSTOM = 'Custom'

    def __str__(self):
        return self.value

    @staticmethod
    def fromstr(cat_name):
        try:
            return Category[cat_name.upper()]
        except KeyError:
            pass

        cats = {cat.value: cat for cat in Category}
        try:
            return cats[get_close_matches(capwords(cat_name), cats.keys(), 1, 0.8)[0]]
        except IndexError:
            raise necrobot.exception.ParseException(f'Could not parse `{cat_name}` as a category.')
