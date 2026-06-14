import click
import wandb

from ..utils import handle_api_errors


def _cleanup_runs(
    api: wandb.Api, entity: str, project: str, min_runtime: int, delete: bool
) -> None:
    """Core logic to clean up short-lived runs."""
    runs = api.runs(f"{entity}/{project}", per_page=200)

    invalid = []
    for run in runs:
        if run.state in ("finished", "running"):
            continue
        runtime = run.summary.get("_runtime") or 0
        if runtime < min_runtime:
            invalid.append((run, runtime))

    if not invalid:
        print("No invalid runs found.")
        return

    print(f"{'ID':<12} {'Name':<40} {'State':<10} {'Runtime':>10}")
    print("-" * 76)
    for run, runtime in invalid:
        print(f"{run.id:<12} {run.name:<40} {run.state:<10} {runtime:>9}s")
    print(f"\nTotal: {len(invalid)} run(s)")

    if not delete:
        print("\nDry run — pass --delete to actually delete.")
        return

    confirm = input(f"\nDelete {len(invalid)} run(s)? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    for run, _ in invalid:
        run.delete()
        print(f"Deleted {run.id} ({run.name})")


def _list_runs(api: wandb.Api, entity: str, project: str, limit: int) -> None:
    """Core logic to list runs."""
    runs = api.runs(f"{entity}/{project}", order="-created_at")
    print(f"{'ID':<12} {'State':<10} {'Name':<40} {'Created':<20} {'Steps':>8}")
    print("-" * 96)
    count = 0
    for run in runs:
        if count >= limit:
            break
        created = run.created_at[:19].replace("T", " ") if run.created_at else "-"
        steps = run.summary.get("_step", "-")
        print(
            f"{run.id:<12} {run.state:<10} {run.name[:40]:<40} {created:<20} {str(steps):>8}"
        )
        count += 1
    if count == 0:
        print(f"No runs found in '{entity}/{project}'")


@click.group()
@click.pass_context
def run(ctx):
    """Manage W&B runs."""
    pass


@run.command()
@click.option(
    "--limit", "-l", default=10, type=int, help="Maximum number of runs to display."
)
@click.pass_context
@handle_api_errors
def list(ctx, limit):
    """List runs."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _list_runs(api, entity, project, limit)


@run.command()
@click.option(
    "--min-runtime",
    default=300,
    type=int,
    show_default=True,
    help="Minimum runtime in seconds; runs below this threshold are considered invalid.",
)
@click.option(
    "--delete", is_flag=True, help="Actually delete the runs (default: dry run)."
)
@click.pass_context
@handle_api_errors
def cleanup(ctx, min_runtime, delete):
    """Delete short-lived runs (crashed/failed/killed) below a runtime threshold."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _cleanup_runs(api, entity, project, min_runtime, delete)


run.add_command(list, name="ls")
