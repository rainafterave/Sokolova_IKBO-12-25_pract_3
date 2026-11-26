"""Execute instructions from a unified code and data memory."""

from codec import decode_at
from instructions import ADD, LOAD, READ, STORE, MEMORY_SIZE, OPCODE_MASK, SPECS
from instructions import MachineError

BYTE_LIMIT = 1 << 8


class VirtualMachine:
    """Store code bytes and integer data cells in one address space."""

    def __init__(self, code, memory_size=MEMORY_SIZE):
        if not 0 < memory_size <= MEMORY_SIZE:
            raise MachineError("invalid memory size")
        if not code or len(code) > memory_size:
            raise MachineError("program is empty or does not fit memory")
        self.memory = [0] * memory_size
        self.memory[:len(code)] = code
        self.program_end = len(code)
        self.pc = 0
        self.accumulator = 0
        self.operations = {
            LOAD: self.load, READ: self.read, STORE: self.store,
            ADD: self.add,
        }

    def check_address(self, address):
        """Require an integer address inside the allocated unified memory."""
        if type(address) is not int or not 0 <= address < len(self.memory):
            raise MachineError(f"memory address out of bounds: {address}")

    def load(self, instruction):
        """Load the immediate B value into the accumulator."""
        self.accumulator = instruction.operand

    def read(self, instruction):
        """Read data at the address currently held in the accumulator."""
        self.check_address(self.accumulator)
        self.accumulator = self.memory[self.accumulator]

    def store(self, instruction):
        """Write the accumulator into the addressed unified-memory cell."""
        self.check_address(instruction.operand)
        self.memory[instruction.operand] = self.accumulator

    def add(self, instruction):
        """Add the addressed data value to the accumulator."""
        self.check_address(instruction.operand)
        self.accumulator += self.memory[instruction.operand]

    def fetch(self):
        """Decode the current memory contents, including earlier code writes."""
        first = self.memory[self.pc]
        if not 0 <= first < BYTE_LIMIT:
            raise MachineError(f"non-byte code cell at address {self.pc}")
        opcode = first & OPCODE_MASK
        if opcode not in SPECS:
            raise MachineError(f"unknown opcode at address {self.pc}: {opcode}")
        end = self.pc + SPECS[opcode].size
        if end > self.program_end:
            raise MachineError(f"truncated instruction at address {self.pc}")
        try:
            code = bytes(self.memory[self.pc:end])
        except (ValueError, TypeError) as error:
            raise MachineError(f"non-byte code at address {self.pc}") from error
        return decode_at(code)

    def run(self):
        """Execute from address zero to the original end of the binary."""
        while self.pc < self.program_end:
            instruction, size = self.fetch()
            operation = self.operations.get(instruction.opcode)
            if operation is None:
                raise MachineError(f"unsupported opcode: {instruction.opcode}")
            operation(instruction)
            self.pc += size
        return self

    def dump(self, start, end):
        """Return all cells in the inclusive range with JSON-friendly keys."""
        self.check_address(start)
        self.check_address(end)
        if start > end:
            raise MachineError("dump start must not exceed dump end")
        return {str(address): self.memory[address]
                for address in range(start, end + 1)}
