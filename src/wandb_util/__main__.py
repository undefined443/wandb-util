import click

from .commands import artifact, log, run


@click.group()
@click.option("--entity", "-e", required=True, help="W&B entity (username or team).")
@click.option("--project", "-p", required=True, help="W&B project name.")
@click.pass_context
def cli(ctx, entity, project):
    """WandB utility tool providing extended functionality."""
    ctx.ensure_object(dict)
    ctx.obj["entity"] = entity
    ctx.obj["project"] = project


cli.add_command(artifact)
cli.add_command(log)
cli.add_command(run)


if __name__ == "__main__":
    cli()
