import random

MEMORY_SIZE = 2048
P_MUTATE = 0.005
OP_NOP = 0
OP_MARK_START = 250
OP_MARK_END = 251
OP_COPY = 252
OP_FIND_EMPTY = 253
OP_ADD = 1
OP_SUB = 2
OP_MUL = 3
OP_DIV = 4
MAX_OP = 254
P_INSERT = 0.002
P_DELETE = 0.002

def wrap(index):
    return index % MEMORY_SIZE

def find_empty_region(length):
    for base in range(MEMORY_SIZE):
        for offset in range(length):
            if memory[wrap(base + offset)] != OP_NOP:
                break
        else:
            return wrap(base)
    return None

def mutate_genome(genome):
    new = []
    for instr in genome:
        if random.random() < P_DELETE:
            continue
        if random.random() < P_INSERT:
            new.append(random.randint(0, MAX_OP))
        if random.random() < P_MUTATE:
            new.append(random.randint(0, MAX_OP))
        else:
            new.append(instr)
    return new

def do_copy(ip):
    reg = registers[ip]
    if 'start' not in reg or 'end' not in reg:
        return
    start = reg['start']
    end = reg['end']
    length = (end - start + MEMORY_SIZE) % MEMORY_SIZE + 1
    genome = [memory[wrap(start + k)] for k in range(length)]
    new_genome = mutate_genome(genome)
    target = random.randint(0, MEMORY_SIZE - 1)
    overlapped = []
    for rid, r2 in registers.items():
        if 'start' in r2 and 'end' in r2:
            s2 = r2['start']
            l2 = (r2['end'] - s2 + MEMORY_SIZE) % MEMORY_SIZE + 1
            positions = {wrap(s2 + i) for i in range(l2)}
            if any(wrap(target + i) in positions for i in range(len(new_genome))):
                overlapped.append(rid)
    for rid in overlapped:
        del registers[rid]
    for k, instr in enumerate(new_genome):
        memory[wrap(target + k)] = instr
    registers[target] = {'start': target, 'end': wrap(target + len(new_genome) - 1)}

def step(ip):
    op = memory[ip]
    reg = registers.setdefault(ip, {})
    if op == OP_MARK_START:
        reg['start'] = ip
    elif op == OP_MARK_END:
        reg['end'] = ip
    elif op == OP_COPY:
        do_copy(ip)
    elif op == OP_FIND_EMPTY:
        if 'start' in reg and 'end' in reg:
            length = (reg['end'] - reg['start'] + MEMORY_SIZE) % MEMORY_SIZE + 1
            reg['empty'] = find_empty_region(length)
    elif op in (OP_ADD, OP_SUB, OP_MUL, OP_DIV):
        a = reg.get('acc', 0)
        b = reg.get('val', 1)
        if op == OP_ADD:
            reg['acc'] = a + b
        elif op == OP_SUB:
            reg['acc'] = a - b
        elif op == OP_MUL:
            reg['acc'] = a * b
        elif op == OP_DIV and b != 0:
            reg['acc'] = a // b

def extract_genome(start, end):
    length = (end - start + MEMORY_SIZE) % MEMORY_SIZE + 1
    return tuple(memory[wrap(start + k)] for k in range(length))

def run_simulation(ticks, report_interval=1000):
    for tick in range(ticks):
        for ip in range(MEMORY_SIZE):
            step(ip)
        if tick % report_interval == 0:
            genomes = []
            for reg in registers.values():
                if 'start' in reg and 'end' in reg:
                    genomes.append(extract_genome(reg['start'], reg['end']))
            if genomes:
                unique = len({g for g in genomes})
                lengths = [len(g) for g in genomes]
                avg_len = sum(lengths) / len(lengths)
                min_len = min(lengths)
                max_len = max(lengths)
                print(f"tick {tick}: population {len(genomes)}, distinct {unique}, length min {min_len}, avg {avg_len:.1f}, max {max_len}")
            else:
                print(f"tick {tick}: no organisms remain")

if __name__ == '__main__':
    memory = [OP_NOP for _ in range(MEMORY_SIZE)]
    registers = {}
    base = random.randint(0, MEMORY_SIZE - 7)
    start = wrap(base)
    a1    = wrap(base + 1)
    a2    = wrap(base + 2)
    a3    = wrap(base + 3)
    a4    = wrap(base + 4)
    end   = wrap(base + 5)
    copy  = wrap(base + 6)
    memory[start] = OP_MARK_START
    memory[a1]    = OP_ADD
    memory[a2]    = OP_MUL
    memory[a3]    = OP_SUB
    memory[a4]    = OP_DIV
    memory[end]   = OP_MARK_END
    memory[copy]  = OP_COPY
    registers[copy] = {'start': start, 'end': end}
    run_simulation(50000, report_interval=500)

