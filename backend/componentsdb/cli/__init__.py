import typer

from . import server

app = typer.Typer()
app.add_typer(server.app, name="server", help="Serve the application over HTTP.")
