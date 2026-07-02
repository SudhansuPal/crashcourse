# crash-course-cs-implemented

Turning the core ideas from **Crash Course Computer Science** into working,
runnable, *from-scratch* code — one concept at a time, building each layer on
the one below it.

## Mission

Most explanations of how computers work stop at the diagram. This project
doesn't. We start with a single boolean and climb, layer by layer, until we
have a working CPU running programs, data structures, algorithms, a file
system, networking, cryptography, and a learning machine — **with no library
that does the thing for us.** We build logic gates from booleans, an adder from
gates, an ALU from the adder, a CPU from the ALU, and so on. If you read this
repo top to bottom, you should be able to explain a computer from the
transistor up.

### Ground rules

- **From first principles.** No importing a library that implements the concept
  we're trying to teach. (We build a hash map without leaning on `dict`
  internals, Huffman coding without a compression lib, RSA without `cryptography`.)
- **Each layer uses the one below it.** The adder is wired from our own gates;
  the ALU from our own adder; the CPU from our own ALU and registers.
- **Heavily commented, runnable, tested.** Every module has a plain-language
  README, a runnable demo, and unit tests where behavior is verifiable.
- **Standard library only.** The concepts have zero third-party dependencies.
  `pytest` is used solely to run the tests.

## Module index

| #  | Module | Concept | Builds on | Status |
|----|--------|---------|-----------|--------|
| 01 | [boolean-logic](01-boolean-logic/) | AND / OR / NOT / XOR from first principles | — | ✅ done |
| 02 | [logic-gates](02-logic-gates/) | Gates from a transistor (switch) model | 01 | ✅ done |
| 03 | [binary-arithmetic](03-binary-arithmetic/) | Binary, two's complement, ripple-carry adder | 02 | ✅ done |
| 04 | [alu](04-alu/) | An Arithmetic Logic Unit wired from gates | 02, 03 | ✅ done |
| 05 | [registers-memory](05-registers-memory/) | Latch → register → addressable RAM | 02 | ✅ done |
| 06 | [cpu](06-cpu/) | Fetch–decode–execute over RAM + registers + ALU | 04, 05 | ✅ done |
| 07 | [instructions](07-instructions/) | An assembler + ISA the CPU runs | 06 | ✅ done |
| 08 | data-structures | Array, linked list, stack, queue, hash map, tree | — | planned |
| 09 | algorithms | Sorting, searching, and Big-O in practice | 08 | planned |
| 10 | file-systems | Block device, inodes, directories, allocation | 08 | planned |
| 11 | compression | Run-length encoding and Huffman coding | 08 | planned |
| 12 | networking | Packets, checksums, a tiny handshake simulation | — | planned |
| 13 | cryptography | Caesar → XOR → Diffie–Hellman → toy RSA | 03 | planned |
| 14 | machine-learning | A perceptron trained with gradient descent | 03 | planned |

> **Modules 01–07 form a complete vertical slice**: a single transistor, built
> up through gates, arithmetic, an ALU, and memory, into a working CPU that runs
> programs written in an assembly language with its own assembler.

> The order intentionally puts **gates before arithmetic and the ALU**, and the
> **CPU before the instruction set**, so every layer can be built from the one
> beneath it instead of being redefined.

Modules are built and reviewed **one at a time**; not every row above exists on
disk yet. Completed modules link to their folder.

## Setup

Requires **Python 3.10+**. No third-party runtime dependencies.

```bash
# (optional) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install pytest so you can run the tests
pip install -r requirements.txt
```

## Running a module

Each module is runnable as a package from the repo root:

```bash
# run a module's demo
python -m 01-boolean-logic.demo      # see the note below about the leading digit

# run the tests for everything
pytest

# run the tests for one module
pytest 01-boolean-logic/
```

> **Note on `python -m` and numeric names:** Python package names can't start
> with a digit, so `python -m 01-boolean-logic.demo` won't import as a package.
> Each module therefore also runs directly as a script:
>
> ```bash
> python 01-boolean-logic/demo.py
> ```
>
> Both the demo and tests are written to work when run directly from the repo
> root. Each module's README shows the exact command.

## License

Educational project — code is meant to be read, run, and taken apart.
