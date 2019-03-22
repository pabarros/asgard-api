from asgard.conf import settings

from .session import _SessionMaker

AsgardDBSession = _SessionMaker(settings.DB_URL, minsize=1)
