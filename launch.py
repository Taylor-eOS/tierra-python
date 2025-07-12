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

def mutate_instruction(instr):
    if random.random() < P_MUTATE:
        return random.randint(0, MAX_OP)
    return instr

def do_copy(ip):
    reg = registers[ip]
    if 'start' not in reg or 'end' not in reg:
        return
    start = reg['start']
    end = reg['end']
    length = (end - start + MEMORY_SIZE) % MEMORY_SIZE + 1
    target = find_empty_region(length)
    if target is None:
        return
    for k in range(length):
        src = wrap(start + k)
        dst = wrap(target + k)
        memory[dst] = mutate_instruction(memory[src])
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

def run_simulation(ticks):
    for tick in range(ticks):
        for ip in range(MEMORY_SIZE):
            step(ip)
        if tick % 1000 == 0:
            alive = sum(1 for r in registers.values() if 'start' in r and 'end' in r)
            print(f"tick {tick}: alive organisms {alive}")

if __name__ == '__main__':
    memory = [OP_NOP for _ in range(MEMORY_SIZE)]
    registers = {}
    base = random.randint(0, MEMORY_SIZE - 3)
    memory[wrap(base    )] = OP_MARK_START
    memory[wrap(base + 1)] = OP_MARK_END
    memory[wrap(base + 2)] = OP_COPY
    registers[wrap(base    )] = {'start': wrap(base    )}
    registers[wrap(base + 1)] = {'end': wrap(base + 1)}
    run_simulation(50000)

