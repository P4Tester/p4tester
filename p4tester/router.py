def convert_ip_to_byte_array(str):
    ip = str.split('.')
    array = []
    for i in ip:
        x = int(i)
        for j in range(8):
            array.append(x / (1 << (7 - j)))
            x = x % (1 << (7 - j))
    return array



class router_rule:
    def __init__(self, match, next_hop, port):
        self.match = match
        self.next_hop = next_hop
        self.port = port

        ipv4 = match.split('/')
        self.prefix = int(ipv4[1])
        self.ip = convert_ip_to_byte_array(ipv4[0])

    def get_prefix(self):
        return self.prefix

    def get_action(self):
        return self.port


class router:
    def __init__(self, name):
        self.rules = []
        self.rule_count = [0 for _ in range(32)]
        self.sort_rules = []
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
        self.rule_count[rule.get_prefix] += 1
        self.sort_rules.append(None)

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

    def sort(self):
        count = [0 for _ in range(32)]
        for i in range(31):
            count[i + 1] = count[i] + self.rule_count[i]

        for r in self.rules:
            pos = count[r.get_prefix()]
            count[r.get_prefix()] += 1
            self.sort_rules[pos] = r

    def get_rule_number(self):
        return len(self.rules)