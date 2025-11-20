import logging.handlers
import os.path
import sys


def _ensure_utf8_stream(stream):
    """Force stdout/stderr to emit UTF-8 so Chinese log lines do not break on Windows."""
    if not stream:
        return
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
            return
        except Exception:
            pass
    # Fallback: best-effort to mark encoding attribute for other handlers.
    if hasattr(stream, "encoding") and stream.encoding is None:
        try:
            stream.encoding = "utf-8"  # type: ignore[attr-defined]
        except Exception:
            pass


_ensure_utf8_stream(sys.stdout)
_ensure_utf8_stream(sys.stderr)

logger = logging.getLogger()
logger.setLevel("INFO")
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler(stream=sys.stdout)
chlr.setFormatter(formatter)
logger.addHandler(chlr)

if not os.path.exists("logs"):
    os.mkdir("logs")
fhlr = logging.handlers.TimedRotatingFileHandler(
    filename="logs/app.log",
    when="D",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
fhlr.setFormatter(formatter)
logger.addHandler(fhlr)
