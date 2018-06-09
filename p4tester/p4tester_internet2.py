from multiprocessing import Pool, cpu_count
from router import router, router_rule
from bdd import bdd, create_true_bdd
from bdd_tree import bdd_tree_node
from router_tree import router_tree_node
import time

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
    c = 0
    for l in f:
        c += 1
        if c > 1000:
            break
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
                break
            ipv4 = match.split('/')
            if len(ipv4) != 2:
                break
            else:
                prefix = int(ipv4[1])
                if prefix > 32 or prefix == 0:
                    break
                ip = ipv4[0].split('.')
                if len(ip) > 4:
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
    router_ports = {}
    next_hop_map = {}
    port_map = {}
    local_ip_map = {}
    for name in internet2_router_names:
        router_ports[name] = []
        f = open('data/Internet2/%s-show_route_forwarding-table_table_default.xml' % name, 'r')
        for _ in range(7):
            f.readline()
        for l in f:
            entry = l.strip('\n').split(' ')
            info = []
            for e in entry:
                if e is not '':
                    info.append(e)
            if len(info) < 5:
                continue
            if l.find('ucst') != -1:
                port = info[-1]
                next_hop = info[-5]
                if port not in router_ports[name]:
                    port_map[port] = name
                    next_hop_map[port] = next_hop
                    router_ports[name].append(port)
            if l.find('locl') != -1:
                local_ip_map[info[3]] = name
    return router_ports, next_hop_map, local_ip_map


def generate_probe(name):
    router = internet2_routers[name]
    bdd_array = []
    for r in router.rules:
        b = bdd(32)
        b.parse_ipv4_prefix(r.match)
        bdd_array.append(b)
    Ha = create_true_bdd(32)
    N = router.get_rule_number()
    rh_array = []
    probe_set = []
    tmp = bdd(32)
    for i in range(N):
        b = bdd(32)
        b.intersection(bdd_array[i], Ha)
        rh_array.append(b)

        tmp.subtract(Ha, bdd_array[i])
        Ha = tmp.copy()
        if b.is_false() is False:
            Hb = b.copy()
            for j in range(i, N):
                override = bdd(32)
                override.intersection(Hb, bdd_array[j])
                if override.is_false() is False:
                    if router.sort_rules[i].get_action() != router.sort_rules[j].get_action():
                        probe_set.append(override)
                    tmp.subtract(Hb, override)
                    Hb = tmp.copy()

            if Hb.is_false() is False:
                print 'Add HB'
                probe_set.append(Hb)
    return probe_set


def generate_probe_simple(name):
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
    tmp = bdd(32)
    for i in range(N):
        b = bdd(32)
        b.intersection(bdd_array[i], Ha)
        rh_array.append(b)
        tmp.subtract(Ha, bdd_array[i])
        Ha = tmp.copy()
        if b.is_false() is False:
            probe_set.append(bdd_array[i])
    return probe_set


def build_bdd_tree(switch_probe_set):
    root = bdd_tree_node(create_true_bdd(32))
    for x in switch_probe_set.keys():
        probe_sets = switch_probe_set[x]
        for p in probe_sets:
            root.insert_child(p, x)

    return root


def bdd_tree_iterate(node, probe_count, router_probe_map, network_probe_sets):
    if isinstance(node, bdd_tree_node) is False:
        print 'Root false'
        exit(1)
    for r in node.router:
        if probe_count not in router_probe_map[r]:
            router_probe_map[r].append(probe_count)
    if len(node.children) == 0:
        network_probe_sets.append(node.bdd)
        probe_count += 1
    else:
        for c in node.children:
            probe_count = bdd_tree_iterate(c, probe_count, router_probe_map, network_probe_sets)
    return probe_count


def get_probe_graph(root):
    if isinstance(root, bdd_tree_node) is False:
        print 'Root false'
        exit(1)
    router_probe_map = {}
    for x in internet2_router_names:
        router_probe_map[x] = []
    network_probe_sets = []
    bdd_tree_iterate(root, 0, router_probe_map, network_probe_sets)
    return router_probe_map, network_probe_sets


def test():
    b1 = create_true_bdd(32)
    b2 = bdd(32)
    b2.parse_ipv4_prefix('3.0.0.0/16')
    b3 = bdd(32)
    b3.intersection(b1, b2)
    # b3.print_bdd()
    # b1.print_bdd()
    # b2.print_bdd()
    print b3.any_sat()


def build_router_tree(root_name, router_ports, next_hop_map, local_ip_map):
    root = router_tree_node(root_name)
    router_map = {}
    for x in internet2_router_names:
        router_map[x] = 0
    router_map[root.name] = 1
    tail = 0
    queue = [root]
    while tail < len(queue):
        node = queue[tail]
        tail += 1
        for p in router_ports[node.name]:
            if p in next_hop_map:
                next_hop = next_hop_map[p]
                if next_hop in local_ip_map:
                    name = local_ip_map[next_hop]
                    if router_map[name] == 0:
                        print name
                        child = router_tree_node(name)
                        node.add_children(child)
                        router_map[name] = 1
                        queue.append(child)
                else:
                    node.add_local_port(p)
    return root


def st_go_through(s, path, router_probe_map, k, probe_path, probe_count):
    for i in router_probe_map[s.name]:
        if len(probe_path[i]) == 0:
            probe_path[i].append(len(path))
        probe_count[i] += 1
        if probe_count[i] >= k:
            probe_path[i].append(len(path))
            probe_count[i] = 0
    for c in s.children:
        path.append((s.name, c.name))
        st_go_through(c, path, router_probe_map, k, probe_path, probe_count)
        path.append((c.name, s.name))


def generate_probe_forwarding_paths(router_root, router_probe_map, k, network_probe_sets):
    path = []
    probe_path = [[] for _ in range(len(network_probe_sets))]
    probe_count = [0 for _ in range(len(network_probe_sets))]
    st_go_through(router_root, path, router_probe_map, k, probe_path, probe_count)

    for i in range(len(network_probe_sets)):
        if probe_count[i] > 0:
            probe_path[i].append(len(path) - 1)

    return path, probe_path


def print_router_tree(root):
    str = ': '
    for c in root.children:
        str += c.name + ','
    print root.name + str
    for c in root.children:
        print_router_tree(c)


def main():
    switch_probe_set = {}
    print 'Generate probes'

    for x in internet2_router_names:
        parse_internet2(x)
        switch_probe_set[x] = generate_probe_simple(internet2_router_names[0])
        print x, len(switch_probe_set[x])

    print 'Build BDD Tree'
    f = time.time()
    root = build_bdd_tree(switch_probe_set)
    print time.time() - f

    print 'Build Probe Map'
    router_probe_map, network_probe_sets = get_probe_graph(root)

    router_ports, next_hop_map, local_ip_map = build_internet2_topology()

    # print local_ip_map

    router_root = build_router_tree('hous', router_ports, next_hop_map, local_ip_map)

    print_router_tree(router_root)
    # exit(1)
    path, probe_path = generate_probe_forwarding_paths(router_root, router_probe_map, 100, network_probe_sets)
    print path
    print probe_path


if __name__ == '__main__':
    main()
