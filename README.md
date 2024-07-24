# voter-tools

[![PyPI](https://img.shields.io/pypi/v/voter-tools.svg)](https://pypi.org/project/voter-tools/)
[![Tests](https://github.com/front-seat/voter-tools/actions/workflows/test.yml/badge.svg)](https://github.com/front-seat/voter-tools/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/front-seat/voter-tools?include_prereleases&label=changelog)](https://github.com/front-seat/voter-tools/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/front-seat/voter-tools/blob/main/LICENSE)

Tools for online voter registration in the United States of America.

Contains a command-line tool (`vote`) and a python library (`voter_tools`) to:

1. Check voter registration status in key states, currently including:
   - Georgia
   - Michigan
   - Pennsylvania
   - Wisconsin
1. Perform online voter registration (OVR) directly with key states, via their APIs. We currently support the [Pennsylvania OVR API](https://www.pa.gov/en/agencies/dos/resources/voting-and-elections-resources/pa-online-voter-registration-web-api-rfc.html) with plans to support Michigan and Washington states in the future.

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
