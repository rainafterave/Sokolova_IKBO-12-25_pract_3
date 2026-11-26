"""Parse an algebraic assembly language into instruction objects."""

import re

from instructions import ADD, LOAD, READ, STORE, Instruction, MachineError
from instructions import validate

PATTERNS = (
    (READ, re.compile(r"ACC\s*=\s*MEM\s*\[\s*ACC\s*\]\s*;")),
    (ADD, re.compile(r"ACC\s*=\s*ACC\s*\+\s*MEM\s*\[\s*(\d+)\s*\]\s*;")),
    (STORE, re.compile(r"MEM\s*\[\s*(\d+)\s*\]\s*=\s*ACC\s*;")),
    (LOAD, re.compile(r"ACC\s*=\s*(\d+)\s*;")),
)


def parse_line(line, number):
    """Parse one instruction and include its line number in errors."""
    for opcode, pattern in PATTERNS:
        match = pattern.fullmatch(line)
        if match:
            operand = int(match[1]) if match.groups() else None
            instruction = Instruction(opcode, operand)
            try:
                validate(instruction)
            except MachineError as error:
                raise MachineError(f"line {number}: {error}") from error
            return instruction
    raise MachineError(f"line {number}: invalid instruction: {line}")


def parse_program(source):
    """Read one semicolon-terminated instruction per non-comment line."""
    program = []
    for number, line in enumerate(source.splitlines(), start=1):
        statement = line.partition("#")[0].strip()
        if statement:
            program.append(parse_line(statement, number))
    if not program:
        raise MachineError("source program is empty")
    return program
