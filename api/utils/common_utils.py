import base64
import csv
import hashlib
import random
import re
import string
from datetime import datetime, timedelta, timezone

from Crypto.Cipher import AES
from flask_apscheduler import APScheduler

from utils.app_config import config


def write_csv(file_path, header, rows):
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f_csv = csv.writer(f, delimiter=',', quotechar='"')
        f_csv.writerow(header)
        f_csv.writerows(rows)


def read_csv(file_path):
    header = []
    res = []
    with open(file_path, "r", encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for item in reader:
            if reader.line_num == 1:
                header = item
                continue
            res.append(dict(zip(header, item)))
        return res


def calc_file_md5(file_path):
    with open(file_path, 'rb') as fp:
        data = fp.read()
    return hashlib.md5(data).hexdigest()


def is_empty(val):
    if val is None or val == "":
        return True
    else:
        return False


def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')


def encrypt(text):
    from utils.app_config import config
    key = config.get('application.key').encode('utf-8')
    text = add_to_16(text)
    cryptos = AES.new(key=key, mode=AES.MODE_ECB)
    cipher_text = cryptos.encrypt(text)
    msg = str(base64.b64encode(cipher_text), encoding="utf8")
    return msg


def decrypt(txt):
    from utils.app_config import config
    key = config.get('application.key').encode('utf-8')
    mode = AES.MODE_ECB
    cryptor = AES.new(key, mode)
    res = base64.decodebytes(txt.encode("utf-8"))
    plain_text = cryptor.decrypt(res).decode("utf-8").rstrip('\0')
    return plain_text


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


def generate_random_string(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def parse_datetime_with_timezone(date_str):
    """
    Parse datetime string with timezone offset and convert to UTC.
    
    Expected format: 2025-11-20T00:44:26.714Z+0100
    - The 'Z' is ignored, the actual timezone is from the offset (+0100)
    - Returns UTC datetime object
    
    Args:
        date_str: Datetime string in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm
        
    Returns:
        datetime object in UTC timezone
    """
    if not date_str:
        return None
    
    # Pattern to match: YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm or YYYY-MM-DDTHH:mm:ssZ+HHmm
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,6}))?Z([+-])(\d{2})(\d{2})'
    match = re.match(pattern, date_str)
    
    if not match:
        # Fallback to standard ISO format parsing
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    date_part = match.group(1)  # YYYY-MM-DDTHH:mm:ss
    fractional = match.group(2) or '0'  # milliseconds/microseconds
    tz_sign = match.group(3)  # + or -
    tz_hours = int(match.group(4))  # HH
    tz_minutes = int(match.group(5))  # mm
    
    # Construct datetime string with fractional seconds
    if len(fractional) <= 3:
        fractional = fractional.ljust(3, '0')
    else:
        fractional = fractional[:6].ljust(6, '0')
    
    dt_str = f"{date_part}.{fractional}"
    
    # Parse the datetime (naive, without timezone)
    try:
        if len(fractional) == 3:
            dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return None
    
    # Calculate timezone offset in minutes
    offset_minutes = (tz_hours * 60 + tz_minutes) * (1 if tz_sign == '+' else -1)
    
    # Convert to UTC by subtracting the offset
    utc_dt = dt - timedelta(minutes=offset_minutes)
    
    return utc_dt.replace(tzinfo=timezone.utc)


def format_utc_datetime_to_db_string(dt):
    """
    Format UTC datetime object to database string format.
    
    Database format: YYYY-MM-DDTHH:mm:ss.SSSZ+0000 (UTC timezone)
    
    Args:
        dt: datetime object (should be UTC)
        
    Returns:
        String in format YYYY-MM-DDTHH:mm:ss.SSSZ+0000
    """
    if dt is None:
        return None
    
    # Ensure it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)
    
    # Format with milliseconds
    milliseconds = dt.microsecond // 1000
    return dt.strftime(f'%Y-%m-%dT%H:%M:%S.{milliseconds:03d}Z+0000')


def get_date_range(time_range, unit="day"):
    current_time = datetime.now()

    from_date = ""
    if unit == "day":
        from_date = current_time - timedelta(days=time_range)
    elif unit.startswith("min"):
        from_date = current_time - timedelta(minutes=time_range)

    def format_date(dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z+0100"

    return format_date(from_date), format_date(current_time)


scheduler = APScheduler()


def get_proxy():
    enable_proxy = config.get("application.proxy.enabled")
    if not enable_proxy:
        return None

    proxy_host = config.get("application.proxy.host")
    proxy_username = config.get("application.proxy.username")
    proxy_password = decrypt(config.get("application.proxy.password"))

    proxies = {
        "http": f"http://{proxy_username}:{proxy_password}@{proxy_host}",
        "https": f"http://{proxy_username}:{proxy_password}@{proxy_host}"
    }
    return proxies


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


# logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
