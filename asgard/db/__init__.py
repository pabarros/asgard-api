from aiopg.sa import create_engine
from hollowman.conf import HOLLOWMAN_DB_URL, HOLLOWMAN_DB_ECHO

from .session import _SessionMaker

AsgardDBSession = _SessionMaker(
    HOLLOWMAN_DB_URL, echo=HOLLOWMAN_DB_ECHO, minsize=1
)
