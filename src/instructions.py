"""Describe instruction fields for the variant 23 virtual machine."""

from dataclasses import dataclass

OPCODE_BITS = 5
LOAD = 7
READ = 26
STORE = 18
ADD = 21
ADDRESS_BITS = 20
CONSTANT_BITS = 23
MEMORY_SIZE = 1 << ADDRESS_BITS
OPCODE_MASK = (1 << OPCODE_BITS) - 1


class MachineError(ValueError):
    """Report an invalid instruction, source program or execution state."""


@dataclass(frozen=True)
class Specification:
    """Define operand width and byte length of a machine instruction."""

    operand_bits: int
    size: int


SPECS = {
    LOAD: Specification(CONSTANT_BITS, 4),
    READ: Specification(0, 1),
    STORE: Specification(ADDRESS_BITS, 4),
    ADD: Specification(ADDRESS_BITS, 4),
}


@dataclass(frozen=True)
class Instruction:
    """Keep numeric A and optional B fields in the intermediate form."""

    opcode: int
    operand: int | None = None

    def fields(self):
        """Return named fields for assembler testing."""
        result = {"A": self.opcode}
        if self.operand is not None:
            result["B"] = self.operand
        return result


def validate(instruction):
    """Check that the opcode and operand fit their specified fields."""
    if instruction.opcode not in SPECS:
        raise MachineError(f"unknown opcode: {instruction.opcode}")
    spec = SPECS[instruction.opcode]
    if instruction.opcode == READ:
        if instruction.operand is not None:
            raise MachineError("READ has no B field")
    elif (
        type(instruction.operand) is not int
        or not 0 <= instruction.operand < (1 << spec.operand_bits)
    ):
        raise MachineError(f"B must fit an unsigned {spec.operand_bits}-bit field")
    return spec
