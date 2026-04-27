import click
import wandb

from ..utils import handle_api_errors


def _list_logs(
    api: wandb.Api,
    entity: str,
    project: str,
    run_id: str,
    show_history: bool = False,
    filter_keys: str | None = None,
    prefix: str | None = None,
    last: int = 10,
) -> None:
    """Core logic to list logs for a run."""
    run = api.run(f"{entity}/{project}/{run_id}")

    print(f"Run:     {run.name} ({run.id})")
    print(f"State:   {run.state}")
    print(f"Project: {entity}/{project}")
    print()

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
def list(ctx, run_id, history, prefix, keys, last):
    """List logs for a run."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _list_logs(api, entity, project, run_id, history, keys, prefix, last)


log.add_command(list, name="ls")
