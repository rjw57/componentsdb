import typer

from . import fakes, import_, server, users

app = typer.Typer()
app.add_typer(server.app, name="server", help="Serve the application over HTTP.")
app.add_typer(users.app, name="users", help="Manage registered users")
app.add_typer(fakes.app, name="fakes", help="Create fake data")
app.add_typer(import_.app, name="import", help="Import existing data")
