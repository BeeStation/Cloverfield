import requests
import time

from cloverfield.db import Player, Ban

# BeeStation Ban API Integration Module.
# Written at fuck-dawn, test this to shit.

# This system only bans by control key, so we're going to be missing SOME people, but this is a good thing to have.

# Datacrafting:

# We can only show one active ban, so we can safely exit on the first ban that matches our criterion.

# We only care about server bans,                                                                   if row["type"] not "server" continue

# Any ban with an unban_date was manually expired,                                                  if row["unban_date"] not None continue

# Any ban that has no unban_date and no expire_date is a permanent ban that has not been raised.    if row["expire_date"] is None return row

# Any ban at this point expires, if we haven't already, cast the current time to an int and save it.

# If the current time is less than expire_date, the ban is still active, continue.

# Else, the ban is valid, and we can break out of the loop.

# We parse out the bee-style ban into something that Goon likes, and pass it off as a permanent clover ban, with a prefix on the description.

# Sample ban: BEE_FORMAT
# {
# "admin": "francinum",
# "ban_date": 1609954788,
# "ckey": "francinum",
# "expire_date": null,
# "global": true,
# "id": 22662,
# "reason": "[TEST_PERM BAN]",
# "round_id": 25795,
# "server": "bs_sage",
# "type": "server",
# "unban_date": 1609954796
# },

# Goon only really needs a few rows, so we can cheat a little.

def fetch_beebans(ply: str):
    """
    Check BeeStation for a valid ban. Only takes ckeys.

    `ply`: Control Key to check, str.

    Returns a jsonify-ready list.
    """
    r = requests.get('https://beestation13.com/api/bans', params={"ckey": ply})
    bans: list = r.json()
    current_time: int = None # Allocate but don't bother calculating this yet.
    active_ban: dict = None # Allocate a holder for the found ban.


    # Determine if we have any active bans.
    for row in bans:
        if row["type"] != "server":
            continue
        if row["unban_date"] is not None:
            continue
        if row["expire_date"] is None:
            active_ban = row
            break
        if current_time is None:
            current_time = int(time.time())
        if current_time < row["expire_date"]:
            continue
        active_ban = row
        break
    if active_ban is None:
        return None

    #Cast the ban into goon format.
    final_ban: dict = {
        "reason": f"MIRROR: {active_ban['reason']}",
        "ckey": active_ban["ckey"],
        "oakey": active_ban["admin"],
        "server": "MIRROR", #Shows the ban as local and gives me a trigger value to reference in DM, if I bother.

        # It screams if these don't exist, apparently.
        "ip": "N/A",
        "compID": "N/A",
        "timestamp": 0 # Mirror bans are visually permanent as we don't control them.
    }
    return [1, final_ban]
