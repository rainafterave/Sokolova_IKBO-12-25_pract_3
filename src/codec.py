"""Encode and decode little-endian variant 23 machine instructions."""

from instructions import Instruction, MachineError, OPCODE_BITS, OPCODE_MASK
from instructions import SPECS, validate


def encode(instruction):
    """Pack A into bits 0–4 and B into the following bits."""
    spec = validate(instruction)
    operand = instruction.operand or 0
    word = instruction.opcode | (operand << OPCODE_BITS)
    return word.to_bytes(spec.size, byteorder="little")


def encode_program(program):
    """Concatenate variable-length instructions in source order."""
    return b"".join(encode(instruction) for instruction in program)


def decode_at(code, offset=0):
    """Decode one instruction, rejecting unknown opcodes and padding bits."""
    if not 0 <= offset < len(code):
        raise MachineError(f"instruction offset outside program: {offset}")
    opcode = code[offset] & OPCODE_MASK
    if opcode not in SPECS:
        raise MachineError(f"unknown opcode {opcode} at byte {offset}")
    spec = SPECS[opcode]
    end = offset + spec.size
    if end > len(code):
        raise MachineError(f"truncated instruction at byte {offset}")
    word = int.from_bytes(code[offset:end], byteorder="little")
    if word >> (OPCODE_BITS + spec.operand_bits):
        raise MachineError(f"non-zero reserved bits at byte {offset}")
    operand = word >> OPCODE_BITS if spec.operand_bits else None
    instruction = Instruction(opcode, operand)
    validate(instruction)
    return instruction, spec.size
