import unittest
import Shodan
import Zoomeye
import NSE
import topology

class TestNetworkScripts(unittest.TestCase):

    def test_shodan(self):
        data = Shodan.get_shodan_data('8.8.8.8')
        self.assertIsNotNone(data)

    def test_zoomeye(self):
        data = Zoomeye.get_zoomeye_data('port:80')
        self.assertIsNotNone(data)

    def test_nse(self):
        data = NSE.nse_scan('192.168.1.1')
        self.assertIsNotNone(data)

    def test_topology(self):
        network_data = {
            'A': ['B', 'C'],
            'B': ['A', 'D', 'E'],
            'C': ['A', 'F'],
            'D': ['B'],
            'E': ['B', 'F'],
            'F': ['C', 'E']
        }
        topology_data = topology.bfs_topology('A', network_data)
        G = topology.construct_topology(topology_data)
        self.assertIsNotNone(G)

if __name__ == '__main__':
    unittest.main()
