import click
import wandb

from ..utils import handle_api_errors


def _print_run_header(run, entity: str, project: str) -> None:
    """Print run information header."""
    print(f"Run:     {run.name} ({run.id})")
    print(f"State:   {run.state}")
    print(f"Project: {entity}/{project}")
    print()


def _get_output_log(
    api: wandb.Api,
    entity: str,
    project: str,
    run_id: str,
    tail: int | None = None,
    output_file: str | None = None,
) -> None:
    """Core logic to display run output log."""
    run = api.run(f"{entity}/{project}/{run_id}")
    _print_run_header(run, entity, project)

    output_content = None
    for file in run.files():
        if file.name == "output.log":
            output_content = file.read_text()
            break

    if output_content is None:
        print("No output.log found for this run.")
        return

    lines = output_content.split("\n")

    if tail:
        lines = lines[-tail:]

    content = "\n".join(lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print(f"Output saved to {output_file}")
    else:
        print(content)


def _show_metrics(
    api: wandb.Api,
    entity: str,
    project: str,
    run_id: str,
    show_history: bool = False,
    filter_keys: str | None = None,
    prefix: str | None = None,
    last: int = 10,
) -> None:
    """Core logic to display metrics for a run."""
    run = api.run(f"{entity}/{project}/{run_id}")
    _print_run_header(run, entity, project)

    filter_set = set(filter_keys.split(",")) if filter_keys else None

    if show_history:
        history = run.history()
        if filter_set:
            cols = [c for c in history.columns if c in filter_set or c == "_step"]
        else:
            cols = list(history.columns)

        df = history[cols].tail(last)
        print(df.to_string(index=False))
    else:
        summary = run.summary.items()
        if prefix:
            summary = {k: v for k, v in summary if k.startswith(prefix)}
        else:
            summary = dict(summary)
        if filter_set:
            summary = {k: v for k, v in summary.items() if k in filter_set}

        if not summary:
            print("No metrics found in summary.")
            return

        key_width = max(len(k) for k in summary)
        print(f"{'Metric':<{key_width}}  Value")
        print("-" * (key_width + 20))
        for key, value in sorted(summary.items()):
            if isinstance(value, float):
                print(f"{key:<{key_width}}  {value:.6g}")
            else:
                print(f"{key:<{key_width}}  {value}")


@click.group()
@click.pass_context
def log(ctx):
    """Manage W&B logs."""
    pass


@log.command()
@click.argument("run_id")
@click.option("--history", is_flag=True, help="Show history instead of summary.")
@click.option("--prefix", help="Filter summary by key prefix (e.g., eval/, train/).")
@click.option("--keys", "-k", help="Filter by comma-separated keys.")
@click.option(
    "--last",
    "-l",
    default=10,
    type=int,
    help="Show last N history entries (default: 10).",
)
@click.pass_context
@handle_api_errors
def metrics(ctx, run_id, history, prefix, keys, last):
    """Display metrics for a run (summary or history)."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _show_metrics(api, entity, project, run_id, history, keys, prefix, last)


@log.command()
@click.argument("run_id")
@click.option(
    "--tail",
    "-t",
    type=int,
    help="Show only the last N lines.",
)
@click.option(
    "--output",
    "-o",
    type=str,
    help="Save output to file.",
)
@click.pass_context
@handle_api_errors
def output(ctx, run_id, tail, output):
    """Display stdout/stderr output for a run."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _get_output_log(api, entity, project, run_id, tail, output)
