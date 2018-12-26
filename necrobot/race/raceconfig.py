from necrobot.config import Config


class RaceConfig(object):
    def __init__(
            self,
            countdown_length=None, unpause_countdown_length=None,
            incremental_countdown_start=None, finalize_time_sec=None,
            auto_forfeit=0
    ):
        self.countdown_length = Config.COUNTDOWN_LENGTH if countdown_length is None else countdown_length
        self.unpause_countdown_length = Config.UNPAUSE_COUNTDOWN_LENGTH if unpause_countdown_length is None else unpause_countdown_length
        self.incremental_countdown_start = Config.INCREMENTAL_COUNTDOWN_START if incremental_countdown_start is None else incremental_countdown_start
        self.finalize_time_sec = Config.FINALIZE_TIME_SEC if finalize_time_sec is None else finalize_time_sec
        self.auto_forfeit = auto_forfeit
