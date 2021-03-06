from necrobot.botbase import cmd_admin
from necrobot.spelunky import cmd_role
from necrobot.race import cmd_racestats
from necrobot.user import cmd_user

from necrobot.botbase.botchannel import BotChannel


class PMBotChannel(BotChannel):
    def __init__(self):
        BotChannel.__init__(self)
        self.channel_commands = [
            cmd_admin.Die(self),
            cmd_admin.Reboot(self),
            cmd_admin.RedoInit(self),

            cmd_racestats.Fastest(self),
            cmd_racestats.MostRaces(self),
            cmd_racestats.Stats(self),

            cmd_user.RaceAlert(self),
            cmd_user.SetInfo(self),
            cmd_user.Timezone(self),
            cmd_user.Twitch(self),
            cmd_user.ViewPrefs(self),
            cmd_user.UserInfo(self),
        ]
