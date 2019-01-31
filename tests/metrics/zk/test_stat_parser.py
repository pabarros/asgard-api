from unittest import TestCase
from hollowman.metrics.zk.parser import parse_stat_output


class TestStatCommandOutputParser(TestCase):
    def setUp(self):
        self.raw_output = """
Zookeeper version: 3.4.10-39d3a4f269333c922ed3db283be479f9deacaa0f, built on 03/23/2017 10:13 GMT\nClients:\n /10.168.200.97:29183[1](queued=0,recved=358786,sent=358787)\n /10.168.200.92:47786[1](queued=0,recved=357625,sent=357625)\n /10.168.200.96:36402[1](queued=0,recved=45488,sent=45488)\n /10.168.200.97:29181[1](queued=0,recved=358786,sent=358787)\n /10.168.200.97:29187[1](queued=0,recved=358787,sent=358788)\n /10.168.200.97:29191[1](queued=0,recved=1287216,sent=1287216)\n /10.168.200.97:29179[1](queued=0,recved=359721,sent=359722)\n /10.168.200.93:35586[1](queued=0,recved=357693,sent=357693)\n /10.168.200.97:29185[1](queued=0,recved=358789,sent=358790)\n /10.168.69.87:49252[0](queued=0,recved=1,sent=0)\n /10.168.200.97:29193[1](queued=0,recved=358783,sent=358783)\n\nLatency min/avg/max: 0/16/3208\nReceived: 4228466\nSent: 4228470\nConnections: 11\nOutstanding: 0\nZxid: 0x100068b83\nMode: leader\nNode count: 932\n
        """
        self.parsed = parse_stat_output(self.raw_output)

    def test_parse_latency(self):
        self.assertEqual(0, self.parsed["latency_min"])
        self.assertEqual(16, self.parsed["latency_avg"])
        self.assertEqual(3208, self.parsed["latency_max"])

    def test_parse_mode(self):
        self.assertEqual("leader", self.parsed["mode"])
        self.assertEqual(1, self.parsed["is_leader"])

    def test_parse_connections(self):
        self.assertEqual(11, self.parsed["connections"])

    def test_parse_oustanding(self):
        self.assertEqual(0, self.parsed["outstanding"])

    def test_parse_node_count(self):
        self.assertEqual(932, self.parsed["node_count"])
