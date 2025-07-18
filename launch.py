import random

MEMORY_SIZE = 2048
P_MUTATE = 0.005
P_INSERT = 0.003
P_DELETE = 0.001
OP_NOP = 0
OP_MARK_START = 250
OP_MARK_END = 251
OP_COPY = 252
OP_FIND_EMPTY = 253
OP_ADD = 1
OP_SUB = 2
OP_MUL = 3
OP_DIV = 4
MAX_OP = OP_FIND_EMPTY
DEATH_THRESHOLD = 0.5

def initialize():
    global memory, registers
    memory = [OP_NOP] * MEMORY_SIZE
    registers = {}

def diffuse():
    pass

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
    length = len(new_genome)
    target = random.randrange(MEMORY_SIZE)
    occ = registers.get(target)
    if occ and 'start' in occ and 'end' in occ:
        old_start = occ['start']
        old_end = occ['end']
        for k in range((old_end - old_start) % MEMORY_SIZE + 1):
            memory[wrap(old_start + k)] = OP_NOP
        del registers[target]
    for k, instr in enumerate(new_genome):
        memory[wrap(target + k)] = instr
    registers[target] = {'start': target, 'end': wrap(target + length - 1)}

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
            length = (reg['end'] - reg['start']) % MEMORY_SIZE + 1
            pos = find_empty_region(length)
            if pos is not None:
                reg['empty'] = pos

def extract_genome(start, end):
    length = (end - start + MEMORY_SIZE) % MEMORY_SIZE + 1
    return tuple(memory[wrap(start + k)] for k in range(length))

def run_simulation(ticks, report_interval=1000):
    initialize()
    base = random.randrange(0, MEMORY_SIZE - 7)
    start, end = base, base + 5
    ops = [OP_MARK_START, OP_ADD, OP_MUL, OP_SUB, OP_DIV, OP_MARK_END, OP_COPY]
    for i, o in enumerate(ops):
        memory[(base + i) % MEMORY_SIZE] = o
    registers[(base + 6) % MEMORY_SIZE] = {'start': start, 'end': end}
    for t in range(ticks):
        for ip in range(MEMORY_SIZE):
            step(ip)
        if t % report_interval == 0:
            pop = [tuple(memory[(r['start'] + k) % MEMORY_SIZE] for k in range((r['end'] - r['start']) % MEMORY_SIZE + 1))
                   for r in registers.values() if 'start' in r and 'end' in r]
            if pop:
                print(f"tick {t}: pop {len(pop)}, distinct {len(set(pop))}")
            else:
                print(f"tick {t}: extinction")

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
