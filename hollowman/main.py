#encoding: utf-8

from hollowman.app import application
import hollowman.routes

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)
