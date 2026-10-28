import random

# game ids from discord's detectable games catalog
GAME_IDS = [
    "401518684763586560",   # apex (legacy)
    "356875570916753438",   # league
    "542179385775894528",   # valorant (legacy)
    "216881337732333568",   # overwatch
    "356875221078245376",   # minecraft (legacy)
    "401518684763586561",
    "356875570916753440",
    "216881337732333570",
    "432980957394370581",
    "356875221078245378",
    "542179385775894530",
    "401518684763586562",
]

MAX_HOURS_PER_CLAIM = 6.0
MIN_HOURS = 0.5


def pick_batch(used, count):
    """Return up to `count` game ids not in `used`."""
    available = [g for g in GAME_IDS if g not in used]
    if not available:
        return []
    random.shuffle(available)
    return available[:count]


def random_hours():
    """Return a random playtime increment in hours."""
    return round(random.uniform(MIN_HOURS, MAX_HOURS_PER_CLAIM), 2)