from multiprocessing import Pool, cpu_count
from router import router, router_rule
from bdd import bdd, create_true_bdd

internet2_routers = {}
internet2_port_map = {}

internet2_router_names = [
    'atla',
    'chic',
    'hous',
    'kans',
    'losa',
    'newy32aoa',
    'salt',
    'seat',
    'wash'
]


def parse_internet2(router_name):
    global internet2_routers
    f = open('data/Internet2/%s-show_route_forwarding-table_table_default.xml'%router_name, 'r')
    r = router(router_name)
    internet2_routers[router_name] = r
    for _ in range(7):
        f.readline()
    match = None
    flag = False
    for l in f:
        if l.find(':') != -1:
            continue
        if l.find('default.iso') != -1:
            break
        entry = l.strip('\n').split(' ')

        info = []
        for e in entry:
            if e is not '':
                info.append(e)

        if flag:
            flag = False
            if len(info) < 5:
                continue
            port = info[-1]
            next_hop = info[-5]
            r.add_peer_port(port, next_hop)
            r.add_rule(router_rule(match, next_hop, port))
        else:
            if len(info) < 5:
                continue
            match = info[0]
            if match.find('-') != -1:
                print match
                break
            ipv4 = match.split('/')
            if len(ipv4) != 2:
                print match
                break
            else:
                prefix = int(ipv4[1])
                if prefix > 32 or prefix == 0:
                    print match
                    break
                ip = ipv4[0].split('.')
                if len(ip) > 4:
                    print ip
                    break

            if info[3] == 'indr':
                flag = True
            elif info[4] == 'locl':
                r.add_local_ip(entry[3])
            elif info[4] == 'ucst':
                port = info[-1]
                next_hop = info[-5]
                r.add_rule(router_rule(match, next_hop, port))
                r.add_local_port(port, next_hop)
            else:
                pass
    r.sort()
    f.close()


def build_internet2_topology():
    global internet2_router_names, internet2_routers
    for name in internet2_router_names:
        r = internet2_routers[name]
        for port in r.get_peer_ports():
            next_hop = r.get_next_hop(port)
            flag_success = False
            for tmp in internet2_router_names:
                if tmp != name and internet2_routers[tmp].check_local_ip(next_hop):
                    r.add_link(port, next_hop, internet2_routers[tmp])
                    flag_success = True
                    break
            if flag_success is False:
                print 'Port not found: ' + port
                exit(1)


def generate_probe(name):
    router = internet2_routers[name]
    bdd_array = []
    for r in router.sort_rules:
        b = bdd(32)
        b.parse_ipv4_prefix(r.match)
        bdd_array.append(b)
    Ha = create_true_bdd(32)
    N = router.get_rule_number()
    rh_array = []
    probe_set = []
    for i in range(N):
        b = bdd(32)
        b.intersection(bdd_array[i], Ha)
        rh_array.append(b)
        tmp = bdd(32)
        tmp.subtract(Ha, bdd_array[i])
        Ha = tmp.copy()
        if b.is_false() is not False:
            Hb = b.copy()
            for j in range(i, N):
                override = bdd(32)
                override.intersection(Hb, bdd_array[j])
                if override.is_false() is not False:
                    if router.sort_rules[i].get_action() != router.sort_rules[j].get_action():
                        probe_set.append(override)
                tmp = bdd(32)
                tmp.subtract(Hb, override)
                Hb = tmp.copy()
    return probe_set


def test():
    b1 = bdd(32)
    b1.parse_ipv4_prefix('3.0.0.0/8')
    b2 = bdd(32)
    b2.parse_ipv4_prefix('3.0.0.0/16')
    b3 = bdd(32)
    b3.intersection(b1, b2)
    b3.print_bdd()
    print b3.any_sat()


def main():
    for x in internet2_router_names:
        parse_internet2(x)
    # build_internet2_topology()
    print len(generate_probe(internet2_router_names[0]))


if __name__ == '__main__':
    main()