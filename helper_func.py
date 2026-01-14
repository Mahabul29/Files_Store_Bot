import base64
import re
from pyrogram import filters

# Fix for the SyntaxWarning at line 77
pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"

async def is_subscribed(filter, client, update):
    # This remains unchanged
    return True 

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    # Logic moved above the return statement to fix the logic flow
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        # Fixed Indentation: These lines now have exactly 8 spaces
        time_list.append(int(result))
        seconds = int(remainder)

    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time

def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def decode(base64_string):
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

subscribed = filters.create(is_subscribed)
