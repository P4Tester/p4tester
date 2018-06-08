class bdd:
    def __init__(self):
        self.end = [0, 1]
        self.bits = []

    def convert_ip_to_byte_array(self, str):
        ip = str.split('.')
        array = []
        for i in ip:
            x = int(i)
            for j in range(8):
                array.append(x / (1<<(7-j)))
                x = x % (1<<(7-j))
        return array


    def parse_ipv4_prefix(self, str):
        ipv4 = str.split('/')
        ip = self.convert_ip_to_byte_array(ipv4[0])
        prefix = ipv4[1]
        for i in range(prefix):
            if ip[i] == 1:
                self.bits.append((-1, i + 1))
            else:
                self.bits.append((i + 1, -1))

        for i in range(prefix, 32):
            self.bits.append((i + 1, i + 1))

    def complement(self):
        x = self.end[0]
        self.end[0] = self.end[1]
        self.end[1] = x