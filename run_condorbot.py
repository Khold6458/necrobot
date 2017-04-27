from necrobot.condor.condoradminchannel import CondorAdminChannel
from necrobot.condor.condormainchannel import CondorMainChannel
from necrobot.condor.condormgr import CondorMgr
from necrobot.condor.condorpmchannel import CondorPMChannel
from necrobot.ladder import ratingutil
from necrobot.league.leaguemgr import LeagueMgr
from necrobot.match.matchmanager import MatchManager
from necrobot.util import console
from necrobot import logon


async def load_condorbot_config(necrobot):
    # PM Channel
    necrobot.register_pm_channel(CondorPMChannel())

    # Main Channel
    main_discord_channel = necrobot.find_channel('season5')
    if main_discord_channel is None:
        console.warning('Could not find the "{0}" channel.'.format('season5'))
    necrobot.register_bot_channel(main_discord_channel, CondorMainChannel())

    # Admin channel
    condor_admin_channel = necrobot.find_channel('adminchat')
    if condor_admin_channel is None:
        console.warning('Could not find the "{0}" channel.'.format('adminchat'))
    necrobot.register_bot_channel(condor_admin_channel, CondorAdminChannel())

    # Managers
    necrobot.register_manager(CondorMgr())
    necrobot.register_manager(LeagueMgr())
    necrobot.register_manager(MatchManager())

    # Ratings
    ratingutil.init()


if __name__ == "__main__":
    logon.logon(
        config_filename='data/condorbot_config',
        load_config_fn=load_condorbot_config
    )
