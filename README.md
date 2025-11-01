# GPU Util Dummy

A utility script to keep GPUs busy. This is needed to avoid the job being killed by the scheduler.

## Requirements

- Python 3.8 or higher
- CUDA-enabled GPU
- uv (Python package manager)

## Installation

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install dependencies

```bash
uv sync
```

## Usage

### Basic run (infinite execution)

```bash
uv run python gpurunner.py
```

Or use the start.sh script:

```bash
chmod +x start.sh
./start.sh
```

### Run for a specific duration

```bash
uv run python gpurunner.py --hours-to-run 2
```

### Options

- `--hours-to-run`: Hours to run. If not specified, runs indefinitely
- `--sleep-time`: Sleep time between operations (default: 0.0005)
- `--matrix-size`: Matrix size for computation (default: 3000)

### Examples

Run for 2 hours with adjusted GPU utilization:

```bash
./start.sh --hours-to-run 2 --sleep-time 0.001
```

## Stopping

You can stop the running process with `Ctrl+C`.

