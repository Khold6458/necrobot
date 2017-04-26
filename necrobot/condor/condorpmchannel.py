from necrobot.match import cmd_match
from necrobot.stats import cmd_stats
from necrobot.user import cmd_user

from necrobot.botbase.botchannel import BotChannel


class CondorPMChannel(BotChannel):
    def __init__(self):
        BotChannel.__init__(self)
        self.channel_commands = [
            cmd_match.Vod(self),

            cmd_stats.LeagueFastest(self),
            cmd_stats.LeagueStats(self),

            cmd_user.SetInfo(self),
            cmd_user.Timezone(self),
            cmd_user.Twitch(self),
            cmd_user.UserInfo(self),
        ]
