import random
import string

alphabet = string.ascii_lowercase + string.digits


def get_new_seed():
    return ':' + ''.join(random.choice(alphabet) for _ in range(11))
