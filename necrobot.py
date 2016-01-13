#TODO: maybe a command to .dailyseed should not register for the new daily if you've yet to complete old one?

import asyncio
import discord
import seedgen
import sqlite3

import daily
import racemgr
import raceinfo

MAIN_CHANNEL_NAME = 'necrobot_main'                         
DAILY_DB_FILENAME = 'data/daily.db'
RACE_DB_FILENAME = 'data/races.db'
BOT_COMMAND_PREFIX = '.'                                    #the prefix used for all bot commands
HELP_INFO = {
    "help":"`.help`: Help.",
    "dailyseed":"`.dailyseed`: Register for today's speedrun daily. You will receive today's seed via PM.",
    "dailystatus":"`.dailystatus`: Find out whether you've submitted to today's daily.",
    "dailysubmit":"`.dailysubmit`: Submit a result for your most recent daily. Daily submissions close an hour after the next " \
                    "daily opens. If you complete the game during the daily, submit your time in the form [m]:ss.hh, e.g.: " \
                    "`.dailysubmit 12:34.56`. If you die during the daily, you may submit your run as `.dailysubmit death` " \
                    "or provide the level of death, e.g. `.dailysubmit death 4-4` for a death on dead ringer.",
    "dailywhen":"`.dailywhen`: Get the date for the current daily, and the time until the next daily opens.",
    "make":"`.make`: Create a new race room. By default this creates a seeded Cadence race (the bot will generate a seed), " \
                    "but you can add the following parameters:\n" \
                    "```\n" \
                    "-u                : Makes an unseeded race.\n" \
                    "-s                : Makes an seeded race (default).\n" \
                    "-char [character] : Makes a race with the given character.\n" \
                    "-seed 1234567     : Use the given seed for the race.\n" \
                    "-custom [text]    : Adds the given text as a descriptor to the race (e.g. '4-shrine').\n```" \
                    "For seeded/unseeded and character options, one can also simply type the character name and 'u' or 'unseeded', etc, " \
                    "so for example `.make dove u` or `.make unseeded dove` both make an unseeded Dove race.",
    "randomseed":"`.randomseed`: Get a randomly generated seed.",
    "info":"`.info`: Necrobot version information.",
    }

class Necrobot(object):

    ## Info string
    def infostr():
        return 'Necrobot ver. 0.2.2. See #command_list for a list of commands.'

    ## Barebones constructor
    def __init__(self, client,):
        self._client = client
        self._server = None
        self._admin_id = None
        self._daily_manager = None
        self._race_manager = None

    ## Initializes object; call after client has been logged in to discord
    def post_login_init(self, server_id, admin_id=None):

        self._admin_id = admin_id if admin_id != 0 else None
        
        #set up server
        if self._client.servers:
            for s in self._client.servers:
                if s.id == server_id:
                    self._server = s
        else:
            print('Error: Could not find the server.')
            exit(1)

        #set up daily manager
        daily_db_connection = sqlite3.connect(DAILY_DB_FILENAME)
        self._daily_manager = daily.DailyManager(self._client, daily_db_connection)

        #set up race manager
        race_db_connection = sqlite3.connect(RACE_DB_FILENAME)
        self._race_manager = racemgr.RaceManager(self._client, self._server, race_db_connection)

    ## Log out of discord
    @asyncio.coroutine
    def logout(self):
        yield from self._client.logout()       

    @asyncio.coroutine
    def parse_message(self, message):
        # don't reply to self
        if message.author == self._client.user:
            return

        # don't reply off server
        if not message.server == self._server:
            return

        # check for command prefix
        if not message.content.startswith(BOT_COMMAND_PREFIX):
            return

        # parse the command, depending on the channel it was typed in (this just restricts which commands are available from where)
        if message.channel.name == MAIN_CHANNEL_NAME:
            yield from self.main_channel_command(message)
        else:
            yield from self._race_manager.parse_message(message)

    @asyncio.coroutine
    def main_channel_command(self, message):
        args = message.content.split()
        command = args.pop(0).replace(BOT_COMMAND_PREFIX, '', 1)

        #.die (super-admin only) : Clean up and log out
        if command == 'die' and message.author.id == self._admin_id:
            yield from self.logout()

        #.updatedaily (super-admin only) : Update the daily leaderboard (for debugging)
        elif command == 'updatedaily' and message.author.id == self._admin_id:
            asyncio.ensure_future(self._daily_manager.update_leaderboard(self._daily_manager.today_number()))

        #.help : Quick help reference
        elif command == 'help':
            if len(args) == 1:
                cmd = args[0].lstrip(BOT_COMMAND_PREFIX)
                if cmd in HELP_INFO:
                    asyncio.ensure_future(self._client.send_message(message.channel, HELP_INFO[cmd]))
            else:   
                asyncio.ensure_future(self._client.send_message(message.channel,
                    "See #necrobot_reference for a command list. Type `.help command` for more info on a particular command."))      

        #.dailyseed : Receive (via PM) today's daily seed
        elif command == 'dailyseed':
            dm = self._daily_manager
            user_id = message.author.id
            
            today = dm.today_number()
            today_date = daily.daily_to_date(today)
            if dm.has_submitted(today, user_id):
                asyncio.ensure_future(self._client.send_message(message.channel, "{0}: You have already submitted for today's daily.".format(message.author.mention)))
            else:
                seed = yield from dm.get_seed(today)
                dm.register(today, user_id)
                asyncio.ensure_future(self._client.send_message(message.author, "({0}) Today's Cadence speedrun seed: {1}".format(today_date.strftime("%d %b"), seed)))

        #.dailystatus : Get your current status for the current daily (unregistered, registered, can still submit for yesterday, submitted)
        elif command == 'dailystatus':
            status = ''        
            dm = self._daily_manager
            user_id = message.author.id
            daily_number = dm.registered_daily(user_id)
            days_since_registering = dm.today_number() - daily_number
            submitted = dm.has_submitted(daily_number, user_id)

            if days_since_registering == 1 and not submitted and dm.within_grace_period():
                status = "You have not gotten today's seed, but you are still able to submit for yesterday's daily."
            elif days_since_registering != 0:
                status = "You have not yet registered: Use `.dailyseed` to get today's seed."
            elif submitted:
                status = "You have submitted to the daily."
            else:
                status = "You have not yet submitted to the daily: Use `.dailysubmit` to submit a result."

            asyncio.ensure_future(self._client.send_message(message.channel, '{0}: {1}'.format(message.author.mention, status)))        
    
        #.dailysubmit : Submit a result for your most recently registered daily (if possible)
        elif command == 'dailysubmit':
            dm = self._daily_manager
            user_id = message.author.id
            daily_number = dm.registered_daily(user_id)

            if daily_number == 0:
                asyncio.ensure_future(self._client.send_message(message.channel,
                    "{0}: Please get today's daily seed before submitting (use `.dailyseed`).".format(message.author.mention, daily.daily_to_shortstr(daily_number))))
            elif not dm.is_open(daily_number):
                asyncio.ensure_future(self._client.send_message(message.channel,
                    "{0}: Too late to submit for the {1} daily. Get today's seed with `.dailyseed`.".format(message.author.mention, daily.daily_to_shortstr(daily_number))))
            elif dm.has_submitted(daily_number, user_id):
                asyncio.ensure_future(self._client.send_message(message.channel,
                    "{0}: You have already submitted for the {1} daily.".format(message.author.mention, daily.daily_to_shortstr(daily_number))))
            else:
                submission_string = dm.parse_submission(daily_number, message.author, args)
                if submission_string: # parse succeeded
                    asyncio.ensure_future(self._client.send_message(message.channel,
                        "Submitted for {0}: {1} {2}.".format(daily.daily_to_shortstr(daily_number), message.author.mention, submission_string)))
                    asyncio.ensure_future(dm.update_leaderboard(daily_number))
                else: # parse failed
                    asyncio.ensure_future(self._client.send_message(message.channel,
                        "{0}: I had trouble parsing your submission. Please use one of the forms: `.dailysubmit 12:34.56` or `.dailysubmit death 4-4`.".format(message.author.mention)))

        #.dailywhen : Gives time info re the daily
        elif command == 'dailywhen':
            info_str = self._daily_manager.daily_time_info_str()
            asyncio.ensure_future(self._client.send_message(message.channel, info_str))

        #.make : create a new race room
        elif command == 'make':
            race_info = raceinfo.parse_args(args)
            if race_info:
                race_channel = yield from self._race_manager.make_race(race_info)
                if race_channel:
                    asyncio.ensure_future(self._client.send_message(message.channel,
                        'A new race has been started by {0}:\nFormat: {2}\nChannel: {1}'.format(message.author.mention, race_channel.mention, race_info.format_str())))
            
        #.randomseed : Generate a new random seed
        elif command == 'randomseed':
            seed = seedgen.get_new_seed()
            asyncio.ensure_future(self._client.send_message(message.channel, 'Seed generated for {0}: {1}'.format(message.author.mention, seed)))       

        
        
  
