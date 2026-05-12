import click
import wandb

from .commands import artifact, log, run


@click.group()
@click.option(
    "--entity",
    "-e",
    default=None,
    help="W&B entity (username or team). Defaults to the entity in ~/.netrc.",
)
@click.option("--project", "-p", required=True, help="W&B project name.")
@click.pass_context
def cli(ctx, entity, project):
    """WandB utility tool providing extended functionality."""
    ctx.ensure_object(dict)
    if entity is None:
        entity = wandb.Api().default_entity
        if entity is None:
            raise click.UsageError(
                "Could not determine entity from credentials. Please specify --entity."
            )
    ctx.obj["entity"] = entity
    ctx.obj["project"] = project


cli.add_command(artifact)
cli.add_command(log)
cli.add_command(run)


if __name__ == "__main__":
    cli()
