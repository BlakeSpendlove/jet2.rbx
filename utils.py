# utils.py

import random
import string
from datetime import datetime

def generate_footer():
    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
    return f"ID: {unique_id} • Logged: {timestamp}", unique_id

