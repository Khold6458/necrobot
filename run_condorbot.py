from necrobot.util import server
from necrobot.condorbot.condoradminchannel import CondorAdminChannel
from necrobot.condorbot.condormainchannel import CondorMainChannel
from necrobot.condorbot.condormgr import CondorMgr
from necrobot.condorbot.condorpmchannel import CondorPMChannel
from necrobot.ladder import ratingutil
from necrobot.league.leaguemgr import LeagueMgr
from necrobot.match.matchmgr import MatchMgr
from necrobot.util import console
from necrobot.config import Config
from necrobot import logon


async def load_condorbot_config(necrobot):
    # PM Channel
    necrobot.register_pm_channel(CondorPMChannel())

    # Main Channel
    server.main_channel = server.find_channel(channel_name=Config.MAIN_CHANNEL_NAME)
    if server.main_channel is None:
        console.warning(f'Could not find the "{Config.MAIN_CHANNEL_NAME}" channel.')
    necrobot.register_bot_channel(server.main_channel, CondorMainChannel())

    # Admin channel
    condor_admin_channel = server.find_channel(channel_name=Config.ADMIN_CHANNEL_NAME)
    if condor_admin_channel is None:
        console.warning(f'Could not find the "{Config.ADMIN_CHANNEL_NAME}" channel.')
    necrobot.register_bot_channel(condor_admin_channel, CondorAdminChannel())

    # Managers (Order is important!)
    necrobot.register_manager(LeagueMgr())
    necrobot.register_manager(MatchMgr())
    necrobot.register_manager(CondorMgr())

    # Ratings
    ratingutil.init()


if __name__ == "__main__":
    logon.logon(
        config_filename='data/condorbot.json',
        logging_prefix='condorbot',
        load_config_fn=load_condorbot_config
    )
