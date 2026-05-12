# wandb-util

A utility tool providing extended functionality for [W&B (Weights & Biases)](https://wandb.ai/).

## Installation

```bash
pip install wandb-util
```

## Features

**run - Manage W&B runs**

```bash
# List runs in a project
wandb-util -e <entity> -p <project> run list [--limit 10]
```

**log - Manage W&B logs**

```bash
# List run summary metrics (filtered by prefix)
wandb-util -e <entity> -p <project> log list <run_id> [--prefix eval/]

# Show training history
wandb-util -e <entity> -p <project> log list <run_id> --history [--last 10]

# Filter by specific keys
wandb-util -e <entity> -p <project> log list <run_id> --keys loss,accuracy
```

**artifact - Manage W&B artifacts**

```bash
# List artifacts for a run
wandb-util -e <entity> -p <project> artifact list <run_id>

# Download an artifact
wandb-util -e <entity> -p <project> artifact download <artifact_path>
```

## Global Options

- `-e, --entity TEXT` - W&B entity (username or team). Defaults to the entity inferred from `~/.netrc` credentials
- `-p, --project TEXT` - W&B project name [required]

## Authentication

wandb-util automatically reads API credentials from `~/.netrc`:

```
machine api.wandb.ai
  login user
  password <your_api_token>
```

## License

MIT
