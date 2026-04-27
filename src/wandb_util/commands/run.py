import click
import wandb

from ..utils import handle_api_errors


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


run.add_command(list, name="ls")
