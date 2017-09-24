from marathon import MarathonApp

from hollowman.log import logger


class DummyLogFilter:
    def read(self, user, request_app: MarathonApp, app: MarathonApp) -> MarathonApp:
        logger.info({'info': 'Im a dummy filter', 'app': request_app})
        return request_app

