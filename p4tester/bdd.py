class bdd:
    def __init__(self):
        self.end = [0, 1]

    def parse_ipv4_prefix(self, str):
        ipv4 = str.split('/')

    def complexment(self):
        x = self.end[0]
        self.end[0] = self.end[1]
        self.end[1] = x