G = [[-1 for _ in range(34)] for _ in range(34)]

class bdd:
    def __init__(self, N):
        self.end = [0, 1]
        self.T = []
        self.N = N
        self.T.append([0, 0, 0])
        self.T.append([1, 1, 1])
        self.T[0][0] = N + 1
        self.T[1][0] = N + 1
        for i in range(N):
            self.T.append([N-i, 0, 0])

    def get_N(self):
        return self.N

    def convert_ip_to_byte_array(self, str):
        ip = str.split('.')
        array = []
        if self.N > 32:
            print str
        for i in ip:
            x = int(i)
            for j in range(8):
                array.append(x / (1<<(7-j)))
                x = x % (1<<(7-j))
        return array

    def parse_ipv4_prefix(self, str):
        ipv4 = str.split('/')
        ip = self.convert_ip_to_byte_array(ipv4[0])
        prefix = int(ipv4[1])
        for i in range(prefix):
            if ip[i] == 1:
                self.T[self.N + 1 - i][1] = 0
                self.T[self.N + 1 - i][2] = self.N - i
            else:
                self.T[self.N + 1 - i][1] = self.N - i
                self.T[self.N + 1 - i][2] = 0

        for i in range(prefix, self.N):
            self.T[self.N + 1 - i][1] = self.N - i
            self.T[self.N + 1 - i][2] = self.N - i

    def mk(self, var, l, h):
        if l is None:
            print var
            exit(1)
        if l == h:
            return l
        u = self.get_u(var)
        self.T[u][0] = var
        self.T[u][1] = l
        self.T[u][2] = h
        return u

    def apply_op(self, op, b1, b2, u1=-1, u2=-1):
        global G
        for i in range(34):
            for j in range(34):
                G[i][j] = -1
        if u1 == -1 and u2 == -1:
            u1 = self.N + 1
            u2 = self.N + 1
        var1 = b1.get_var(u1)
        var2 = b2.get_var(u2)
        if G[u1][u2] != -1:
            return G[u1][u2]
        elif u1 <= 1 and u2 <= 1:
            if op == '&':
                return u1 & u2
            elif op == '|':
                return u1 | u2
        elif var1 == var2:
            G[u1][u2] = self.mk(var1,
                            self.apply_op(op, b1, b2, b1.get_low(u1), b2.get_low(u2)),
                            self.apply_op(op, b1, b2, b1.get_high(u1), b2.get_high(u2)))

        elif var1 < var2:
            G[u1][u2] = self.mk(var1,
                           self.apply_op(op, b1, b2, b1.get_low(u1), u2),
                           self.apply_op(op, b1, b2, b1.get_high(u1), u2))
        elif var1 > var2:
            G[u1][u2] = self.mk(var2,
                           self.apply_op(op, b1, b2, u1, b2.get_low(u2)),
                           self.apply_op(op, b1, b2, u1, b2.get_high(u2)))
        return G[u1][u2]

    def complement(self):
        for i in range(2, self.N+2):
            if self.T[i][1] == 0:
                self.T[i][1] = 1
            elif self.T[i][1] == 1:
                self.T[i][1] = 0

            if self.T[i][2] == 0:
                self.T[i][2] = 1
            elif self.T[i][2] == 1:
                self.T[i][2] = 0

    def intersection(self, b1, b2):
        global G
        for i in range(34):
            for j in range(34):
                G[i][j] = -1
        self.apply_op('&', b1, b2)

    def subtract(self, b1, b2):
        b2_copy = b2.copy()
        b2_copy.complement()
        self.intersection(b1, b2_copy)

    def union(self,  b1, b2):
        global G
        for i in range(34):
            for j in range(34):
                G[i][j] = -1
        self.apply_op('|', b1, b2)

    def get_u(self, var):
        return len(self.T) - var

    def get_var(self, u):
        return self.T[u][0]

    def get_low(self, u):
        return self.T[u][1]

    def get_high(self, u):
        return self.T[u][2]

    def copy(self):
        b = bdd(self.N)
        for i in range(self.N + 2):
            b.T[i][0] = self.T[i][0]
            b.T[i][1] = self.T[i][1]
            b.T[i][2] = self.T[i][2]
        return b

    def print_bdd(self):
        for i in range(self.N):
            print '%d %d %d %d'%(i+2, self.T[i+2][0], self.T[i+2][1], self.T[i+2][2])

    def is_false(self):
        a = self.any_sat()
        if a is None:
            return True
        else:
            return False

    def any_sat(self, u=-1):
        if u == -1:
            u = self.N + 1
        if u == 0:
            return None
        elif u == 1:
            return []
        elif self.get_low(u) == 0:
            a = self.any_sat(self.get_high(u))
            if a is None:
                return None
            else:
                return [1] + a
        else:
            a = self.any_sat(self.get_low(u))
            if a is None:
                return None
            else:
                return [0] + a


def create_true_bdd(n):
    b = bdd(n)
    for i in range(n):
        b.T.append((n - i, n - i, n - i))
    return b


def create_false_bdd(n):
    b = bdd(n)
    for i in range(n):
        b.T.append((n - i, n - i, n - i))
    b.T[n + 1][1] = 0
    b.T[n + 1][2] = 0
    return b


