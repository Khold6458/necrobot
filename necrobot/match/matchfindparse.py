"""Utility for parsing user-entered strings and finding a corresponding Match"""
import pytz
import shlex

import necrobot.exception
from necrobot.util.parse import dateparse
from necrobot.database import matchdb
from necrobot.match import matchutil
from necrobot.user import userlib

from necrobot.match.match import Match


async def find_match(input_str: str, tz: pytz.timezone = pytz.utc) -> Match:
    """Find a match in the league database corresponding to the input args
    
    Parameters
    ----------
    input_str: str
        A user-input string that we want to use to find a registered match.
    tz: pytz.timezone
        A timezone (used for interpreting dates in the input_str)

    Returns
    -------
    Match
        The found match.
        
    Raises
    ------
    NotFoundException
        If no match could be found.
    ParseException
        If the input string couldn't be parsed meaningfully.
    """
    args = shlex.split(input_str)
    if len(args) < 2:
        raise necrobot.exception.ParseException('Need at least two arguments to find a match.')

    racer_1 = await userlib.get_user(any_name=args[0])
    if racer_1 is None:
        raise necrobot.exception.NotFoundException("Can't find any racer by the name `{0}`.".format(args[0]))
    args.pop(0)

    racer_2 = await userlib.get_user(any_name=args[0])
    if racer_2 is None:
        raise necrobot.exception.NotFoundException("Can't find any racer by the name `{0}`.".format(args[0]))
    args.pop(0)

    match_date = None
    match_date_str = ''
    for arg in args:
        match_date_str += arg + ' '
    if match_date_str:
        match_date_str = match_date_str[:-1]
        match_date = dateparse.parse_datetime(match_date_str, tz)

    match_id = await matchdb.get_match_id(
        racer_1_id=racer_1.user_id,
        racer_2_id=racer_2.user_id,
        scheduled_time=match_date
    )
    if match_id is None:
        raise necrobot.exception.NotFoundException(
            "Can't find any match between `{0}` and `{1}`.".format(racer_1.bot_name, racer_2.bot_name)
        )

    return await matchutil.get_match_from_id(match_id)
