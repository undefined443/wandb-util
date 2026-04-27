from pathlib import Path

import click
import wandb

from ..utils import handle_api_errors


def fmt_size(n_bytes: int) -> str:
    size: float = float(n_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _list_artifacts(
    api: wandb.Api, entity: str, project: str, run_id: str, artifact_type: str
) -> None:
    """Core logic to list artifacts for a run."""
    run = api.run(f"{entity}/{project}/{run_id}")
    artifacts = sorted(
        [a for a in run.logged_artifacts() if a.type == artifact_type],
        key=lambda x: x.metadata.get("global_step", 0),
    )

    if not artifacts:
        print(f"No artifacts found for run '{run_id}'")
        return

    print(f"Run: {run.name} ({run_id})  state={run.state}")
    print()
    print(f"{'Version':<28} {'Step':>8} {'Size':>10}  {'Created'}")
    print("-" * 72)
    for a in artifacts:
        step = a.metadata.get("global_step", "-")
        created = a.created_at[:19].replace("T", " ") if a.created_at else "-"
        print(f"{a.name:<28} {str(step):>8} {fmt_size(a.size):>10}  {created}")


def _download_artifact(
    api: wandb.Api, entity: str, project: str, artifact_path: str, output_dir: str
) -> None:
    """Core logic to download an artifact."""
    artifact = api.artifact(f"{entity}/{project}/{artifact_path}", type="model")
    out = Path(output_dir)
    click.echo(f"Downloading {artifact.name} ({fmt_size(artifact.size)}) -> {out}/")
    artifact.download(root=str(out))
    click.echo("Done.")


@click.group()
@click.pass_context
def artifact(ctx):
    """Manage W&B artifacts."""
    pass


@artifact.command()
@click.argument("run_id")
@click.option("--type", "-t", default="model", help="Artifact type (default: model).")
@click.pass_context
@handle_api_errors
def list(ctx, run_id, type):
    """List artifacts for a run."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _list_artifacts(api, entity, project, run_id, type)


artifact.add_command(list, name="ls")


@artifact.command()
@click.argument("artifact_path")
@click.option(
    "--output-dir", "-o", default=".", help="Directory to download into (default: .)."
)
@click.pass_context
@handle_api_errors
def download(ctx, artifact_path, output_dir):
    """Download an artifact."""
    entity = ctx.obj["entity"]
    project = ctx.obj["project"]
    api = wandb.Api()
    _download_artifact(api, entity, project, artifact_path, output_dir)
