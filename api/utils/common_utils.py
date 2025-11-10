import base64
import csv
import hashlib
import random
import string
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from flask_apscheduler import APScheduler


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

# logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)