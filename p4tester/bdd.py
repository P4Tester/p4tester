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
                self.T[33 - i][1] = 0
                self.T[33 - i][2] = 32 - i
            else:
                self.T[33 - i][1] = 32 - i
                self.T[33 - i][2] = 0

        for i in range(prefix, 32):
            self.T[33 - i][1] = 32 - i
            self.T[33 - i][2] = 32 - i

    def mk(self, var, l, h):
        if l is None:
            print var
            exit(1)
        if l == h:
            self.print_bdd()
            exit
            return l
        u = self.get_u(var)
        self.T[u][0] = var
        self.T[u][1] = l
        self.T[u][2] = h
        return u

    def apply_op(self, op, b1, b2, u1=-1, u2=-1):
        if u1 == -1 and u2 == -1:
            u1 = len(b1.T) - 1
            u2 = len(b2.T) - 1
            print u1, u2
        var1 = b1.get_var(u1)
        var2 = b2.get_var(u2)
        if u1 <= 1 and u2 <= 1:
            if op == '&':
                return u1 & u2
            elif op == '|':
                return u1 | u2

        elif var1 == var2:
            return self.mk(var1,
                           self.apply_op(op, b1, b2, b1.get_low(u1), b2.get_low(u2)),
                           self.apply_op(op, b1, b2, b1.get_high(u1), b2.get_high(u2)))
        elif var1 < var2:
            return self.mk(var1,
                           self.apply_op(op, b1, b2, b1.get_low(u1), u2),
                           self.apply_op(op, b1, b2, b1.get_high(u1), u2))
        elif var1 > var2:
            return self.mk(var2,
                           self.apply_op(op, b1, b2, u1, b2.get_low(u2)),
                           self.apply_op(op, b1, b2, u1, b2.get_high(u2)))

    def complement(self):
        for i in self.T[2:]:
            if self.T[i][1] == 0:
                self.T[i][1] = 1
            elif self.T[i][1] == 1:
                self.T[i][1] = 0

            if self.T[i][2] == 0:
                self.T[i][2] = 1
            elif self.T[i][2] == 1:
                self.T[i][2] = 0

    def intersection(self, b1, b2):
        self.apply_op('&', b1, b2)

    def subtract(self, b1, b2):
        b2_copy = b2.copy()
        b2_copy.complement()
        self.intersection(b1, b2_copy)

    def union(self,  b1, b2):
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




def apply_op(op, b1, b2, u1=-1, u2=-1):
    T = []
    T.append((0, 0, 0))
    T.append((1, 1, 1))
    if u1 == -1 and u2 == -1:
        u1 = len(b1.T) -1
        u2 = len(b2.T) - 1
    var1 = b1.get_var(u1)
    var2 = b2.get_var(u2)
    if u1 <= 1 and u2 <= 1:
        if op == '^':
            return
        elif op == '|':
            return
    elif var1 == var2:
        pass
    elif var1 < var2:
        pass
    elif var1 > var2:
        pass
