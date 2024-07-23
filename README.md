# voter-tools

[![PyPI](https://img.shields.io/pypi/v/voter-tools.svg)](https://pypi.org/project/voter-tools/)
[![Tests](https://github.com/front-seat/voter-tools/actions/workflows/test.yml/badge.svg)](https://github.com/front-seat/voter-tools/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/front-seat/voter-tools?include_prereleases&label=changelog)](https://github.com/front-seat/voter-tools/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/front-seat/voter-tools/blob/main/LICENSE)

Tools for online voter registration in the United States of America.

## Installation

Install this library using `pip`:

```bash
pip install voter-tools
```

## Usage

Usage instructions are coming soon.

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

```bash
cd voter-tools
python -m venv .venv
source .venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[dev]'
```

To run tests:

```bash
make test
```

To run a full lint/typecheck/test pass:

```bash
make check
```
