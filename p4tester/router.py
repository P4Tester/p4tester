class router_rule:
    def __init__(self, match, next_hop, port):
        self.match = match
        self.next_hop = next_hop
        self.port = port


class router:
    def __init__(self, name):
        self.rules = []
        self.name = name
        self.peer_ports = []
        self.local_ports = []
        self.next_hop = {}
        self.local_ip = []
        self.port_link = {}
        self.next_hop_link = {}

    def add_peer_port(self, port, next_hop):
        if port not in self.peer_ports:
            self.peer_ports.append(port)
            self.next_hop[port] = next_hop

    def add_local_port(self, port, next_hop):
        if port not in self.local_ports:
            self.local_ports.append(port)
            self.next_hop[port] = next_hop

    def add_local_ip(self, ip):
        if ip not in self.local_ip:
            self.local_ip.append(ip)

    def add_rule(self, rule):
        self.rules.append(rule)

    def add_link(self, port, next_hop, r):
        self.next_hop_link[next_hop] = r
        self.port_link[port] = r

    def get_peer_ports(self):
        return self.peer_ports

    def get_next_hop(self, port):
        return self.next_hop[port]

    def check_local_ip(self, ip):
        if ip in self.local_ip:
            return True
        return False