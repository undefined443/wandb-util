import functools

import click
import wandb


def handle_api_errors(func):
    """Decorator to handle common wandb API errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except wandb.errors.CommError as e:
            click.secho(
                f"Error: Failed to connect to wandb API. {str(e)}", fg="red", err=True
            )
            raise SystemExit(1)
        except wandb.errors.AuthenticationError:
            click.secho(
                "Error: Authentication failed. Check your API key in ~/.netrc",
                fg="red",
                err=True,
            )
            raise SystemExit(1)
        except Exception as e:
            click.secho(f"Error: {str(e)}", fg="red", err=True)
            raise SystemExit(1)

    return wrapper
