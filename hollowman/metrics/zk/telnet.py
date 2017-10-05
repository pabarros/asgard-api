
from telnetlib import Telnet


def send_command(host, port, command):
    conn = Telnet(host.encode("utf8"), port)
    conn.write(command.encode("utf8"))
    return conn.read_all()
