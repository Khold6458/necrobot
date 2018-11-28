import necrobot.exception
from necrobot.botbase.commandtype import CommandType
from necrobot.race import racestats
from necrobot.user import userlib
from necrobot.util import server, strutil
from necrobot.util.category import Category

class Fastest(CommandType):
    def __init__(self, bot_channel):
        CommandType.__init__(self, bot_channel, 'fastest')
        self.help_text = '`.fastest <category>` shows the fastest times for a given category.'

    async def _do_execute(self, cmd):
        await server.client.send_typing(cmd.channel)

        try:
            category = Category.fromstr(cmd.arg_string)
        except necrobot.exception.ParseException as e:
            await self.client.send_message(cmd.channel, e)
            return

        infotext = await racestats.get_fastest_times_infotext(category, 20)
        infobox = 'Fastest public {0} times:\n```\n{1}```'.format(
            category.name,
            strutil.tickless(infotext))
        await self.client.send_message(
            cmd.channel,
            infobox)


class MostRaces(CommandType):
    def __init__(self, bot_channel):
        CommandType.__init__(self, bot_channel, 'mostraces')
        self.help_text = '`.mostraces <category_name>` shows the racers with the largest number of public ' \
                         ' races for that category.'

    async def _do_execute(self, cmd):
        await server.client.send_typing(cmd.channel)

        try:
            category = Category.fromstr(cmd.arg_string)
        except necrobot.exception.ParseException as e:
            await self.client.send_message(cmd.channel, e)
            return

        infotext = await racestats.get_most_races_infotext(category, 20)
        infobox = 'Most public {0} races:\n```\n{1}```'.format(
            category.name,
            strutil.tickless(infotext)
        )
        await self.client.send_message(
            cmd.channel,
            infobox
        )


class Stats(CommandType):
    def __init__(self, bot_channel):
        CommandType.__init__(self, bot_channel, 'stats')
        self.help_text = 'Show your own race stats, or use `.stats <username>` to show for a different user.'

    async def _do_execute(self, cmd):
        await server.client.send_typing(cmd.channel)

        # Parse arguments
        args = cmd.args

        if len(args) > 1:
            await self.client.send_message(
                cmd.channel,
                '{0}: Error: wrong number of arguments for `.stats`.'.format(cmd.author.mention))
            return

        if len(args) == 0:
            user = await userlib.get_user(discord_id=int(cmd.author.id), register=True)
        else:  # len(args) == 1
            racer_name = args[0]
            user = await userlib.get_user(any_name=racer_name)
            if user is None:
                await self.client.send_message(
                    cmd.channel,
                    'Could not find user "{0}".'.format(racer_name))
                return

        # Show stats
        general_stats = await racestats.get_general_stats(user.user_id)
        await self.client.send_message(
            cmd.channel,
            '```\n{0}\'s stats (public races):\n{1}\n```'.format(
                strutil.tickless(user.display_name),
                general_stats.infotext)
        )
