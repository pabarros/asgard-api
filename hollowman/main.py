from hollowman.app import application
import os


if __name__ == "__main__":
    application.run(
        host="0.0.0.0",
        port=int(os.getenv("ASGARD_HTTP_PORT", 5000)),
        debug=True,
        threaded=True,
    )
