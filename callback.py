import settings
import helpers
import struct
import socket
import urllib.parse
import html.parser as htmlparser
import json
from flask import Flask
import app
# This system is terrible.
# I hate it. I hate it. I hate it.
# It's HILARIOUSLY insecure.

async def query_server(game_server:str = settings.ACTIVE_SERVER, game_port:int = settings.ACTIVE_PORT, querystr="?status", bother_parsing:bool = True) -> dict:
    """
    Queries the server for information
    """
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        query = b"\x00\x83" + struct.pack('>H', len(querystr) + 6) + b"\x00\x00\x00\x00\x00" + querystr.encode() + b"\x00" #Creates a packet for byond according to TG's standard
        conn.settimeout(settings.CALLBACK_TIMEOUT) #Byond is slow, timeout set relatively high to account for any latency
        conn.connect((game_server, game_port))

        conn.sendall(query)

        data = conn.recv(4096) #Minimum number should be 4096, anything less will lose data



        if bother_parsing:
            parsed_data = urllib.parse.parse_qs(data[5:-1].decode())
            return parsed_data
        else:
            return 0
        # +----------------+--------+
        # | Reported Items | Return |
        # +----------------+--------+
        # | Version        | str    | SUPORTED NATIVELY
        # | mode           | str    | SUPORTED NATIVELY
        # | respawn        | int    | SUPORTED NATIVELY
        # | enter          | int    | SUPORTED NATIVELY
        # | vote           | int    | SUPORTED NATIVELY
        # | ai             | int    | SUPORTED NATIVELY
        # | host           | str    | SUPORTED NATIVELY
        # | active_players | int    |
        # | players        | int    | SUPORTED NATIVELY
        # | revision       | str    | NOT SUPPORTED
        # | revision_date  | date   | NOT SUPPORTED
        # | admins         | int    | NOT HANDLED
        # | gamestate      | int    | PART OF ROUND DURATION
        # | map_name       | str    | SUPORTED NATIVELY
        # | security_level | str    | NOT A CONCEPT
        # | round_duration | int    | HANDLED ENTIRELY DIFFERENTLY.
        # | shuttle_mode   | str    |
        # | shuttle_timer  | str    | NAMED_DIFFERENTLY (shuttle_time)
        # +----------------+--------+

    except (ConnectionRefusedError, socket.gaierror, socket.timeout):
        return None #Server is likely offline

    finally:
        conn.close()

async def hub_callback(proc: str, data: dict, datum: str=None, secure:bool = False):
    """
    Execute a hub callback.

    MUST NOT have the `/proc/` prefix.

    `datum` seems to never actually be used in production code. Tied to None by default.
    """
    big_ass: dict = {
        "type":"hubCallback",
        "proc": proc,
        "data": json.dumps(data, indent=None, separators=(",",":"))
    }

    if(datum is not None): #Turns out, it flips shit if it gets passed a null datum.
        big_ass.update({"datum": datum})
    if(secure):
        big_ass.update({"auth": settings.API_KEY})
    long_ass_parameters = urllib.parse.urlencode(big_ass)
    return await query_server(querystr=long_ass_parameters, bother_parsing=False) #We don't care about return values on hub callbacks. They return hot garbage anyways.
