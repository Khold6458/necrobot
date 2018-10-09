"""
Interaction with the races, race_types, and race_runs databases (necrobot or condor event schema).
"""

from necrobot.database.dbconnect import DBConnect
from necrobot.database.dbutil import tn
from necrobot.race.race import Race
from necrobot.race.raceinfo import RaceInfo
from necrobot.util.category import Category

# Record a race-------------------------------------------------------------------
async def record_race(race: Race) -> None:
    type_id = await get_race_type_id(race.race_info, register=True)

    async with DBConnect(commit=True) as cursor:
        # Record the race
        race_params = (
            race.start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            type_id,
            race.race_info.seed if race.race_info.seeded else 0,
            race.race_info.condor_race,
            race.race_info.private_race,
        )

        cursor.execute(
            """
            INSERT INTO {0}
                (timestamp, type_id, seed, condor, private)
            VALUES (%s,%s,%s,%s,%s)
            """.format(tn('races')),
            race_params
        )

        # Store the new race ID in the Race object
        cursor.execute("SELECT LAST_INSERT_ID()")
        race.race_id = int(cursor.fetchone()[0])

        # Record each racer in race_runs
        rank = 1
        for racer in race.racers:
            racer_params = (race.race_id, racer.user_id, racer.time, rank, racer.igt, racer.comment, racer.level)
            cursor.execute(
                """
                INSERT INTO {0}
                    (race_id, user_id, time, rank, igt, comment, level)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """.format(tn('race_runs')),
                racer_params
            )
            if racer.is_finished:
                rank += 1


# Race type functions-------------------------------------------------------------------
async def get_race_type_id(race_info: RaceInfo, register: bool = False) -> int or None:
    params = (
        race_info.category.name.lower(),
        race_info.cat_str,
        race_info.seeded
    )

    async with DBConnect(commit=False) as cursor:
        cursor.execute(
            """
            SELECT `type_id`
            FROM `race_types`
            WHERE `category`=%s
               AND `descriptor`=%s
               AND `seeded`=%s
            LIMIT 1
            """,
            params
        )
        row = cursor.fetchone()
        if row is not None:
            return int(row[0])

    # If here, the race type was not found
    if not register:
        return None

    # Create the new race type
    async with DBConnect(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO `race_types`
            (category, descriptor, seeded)
            VALUES (%s, %s, %s)
            """,
            params
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        return int(cursor.fetchone()[0])


async def get_race_info_from_type_id(race_type: int) -> RaceInfo or None:
    params = (race_type,)
    async with DBConnect(commit=False) as cursor:
        cursor.execute(
            """
            SELECT `category`, `descriptor`, `seeded`
            FROM `race_types`
            WHERE `type_id`=%s
            """,
            params
        )

        row = cursor.fetchone()
        if row is not None:
            race_info = RaceInfo(Category.fromstr(row[0]), row[1], row[2])
            return race_info
        else:
            return None


# Stat functions-------------------------------------------------------------------
async def get_public_race_numbers(user_id: int) -> list:
    async with DBConnect(commit=False) as cursor:
        params = (user_id,)
        cursor.execute(
            """
            SELECT `race_types`.`category`, COUNT(*) as num
            FROM {1}
                INNER JOIN {0} ON {0}.`race_id` = {1}.`race_id`
                INNER JOIN race_types ON {0}.`type_id` = `race_types`.`type_id`
            WHERE {1}.`user_id` = %s
                AND NOT {0}.`private`
            GROUP BY `race_types`.`category`
            ORDER BY num DESC
            """.format(tn('races'), tn('race_runs')),
            params)
        return cursor.fetchall()


async def get_all_racedata(user_id: int, cat_name: str) -> list:
    async with DBConnect(commit=False) as cursor:
        params = (user_id, cat_name)
        cursor.execute(
            """
            SELECT {1}.`time`, {1}.`level`
            FROM {1}
                INNER JOIN {0} ON {0}.`race_id` = {1}.`race_id`
                INNER JOIN `race_types` ON {0}.`type_id` = `race_types`.`type_id`
            WHERE {1}.`user_id` = %s
                AND `race_types`.`category` = %s
            AND NOT {0}.`private`
            """.format(tn('races'), tn('race_runs')),
            params
        )
        return cursor.fetchall()


async def get_fastest_times_leaderboard(category_name: str, limit: int) -> list:
    async with DBConnect(commit=False) as cursor:
        params = {'category': category_name, 'limit': limit,}
        cursor.execute(
            """
            SELECT
                users.`discord_name`,
                mintimes.`min_time`,
                {races}.`seed`,
                {races}.`timestamp`
            FROM
                (
                    SELECT user_id, MIN(time) AS `min_time`
                    FROM {race_runs}
                    INNER JOIN {races} ON {races}.`race_id` = {race_runs}.`race_id`
                    INNER JOIN race_types ON race_types.`type_id` = {races}.`type_id`
                    WHERE
                        {race_runs}.time > 0
                        AND {race_runs}.level = -2
                        AND race_types.category=%(category)s
                        AND NOT {races}.private
                    GROUP BY user_id
                ) mintimes
            INNER JOIN {race_runs} ON ({race_runs}.`user_id` = mintimes.`user_id` AND {race_runs}.`time` = mintimes.`min_time`)
            INNER JOIN {races} ON {races}.`race_id` = {race_runs}.`race_id`
            INNER JOIN race_types ON race_types.`type_id` = {races}.`type_id`
            INNER JOIN users ON users.`user_id` = mintimes.`user_id`
            WHERE
                {race_runs}.`level` = -2
                AND race_types.category=%(category)s
                AND NOT {races}.`private`
            GROUP BY {race_runs}.`user_id`
            ORDER BY mintimes.min_time ASC
            LIMIT %(limit)s
            """.format(races=tn('races'), race_runs=tn('race_runs')),
            params)
        return cursor.fetchall()


async def get_most_races_leaderboard(category_name: str, limit: int) -> list:
    async with DBConnect(commit=False) as cursor:
        params = (category_name, limit,)
        cursor.execute(
            """
            SELECT
                user_name,
                num_races
            FROM
            (
                SELECT
                    users.discord_name as user_name,
                    SUM(
                            IF(
                               race_types.category=%s
                               AND NOT {0}.private,
                               1, 0
                            )
                    ) as num_races
                FROM {1}
                    INNER JOIN users ON users.user_id = {1}.user_id
                    INNER JOIN {0} ON {0}.race_id = {1}.race_id
                    INNER JOIN race_types ON race_types.type_id = {0}.type_id
                GROUP BY users.discord_name
            ) tbl1
            ORDER BY num_races DESC
            LIMIT %s
            """.format(tn('races'), tn('race_runs')),
            params)
        return cursor.fetchall()


async def get_largest_race_number(user_id: int) -> int:
    async with DBConnect(commit=False) as cursor:
        params = (user_id,)
        cursor.execute(
            """
            SELECT race_id
            FROM {0}
            WHERE user_id = %s
            ORDER BY race_id DESC
            LIMIT 1
            """.format(tn('race_runs')),
            params)
        row = cursor.fetchone()
        return int(row[0]) if row is not None else 0
