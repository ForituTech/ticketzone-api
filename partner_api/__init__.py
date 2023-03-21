import pathlib

from starlette.templating import Jinja2Templates

templates = Jinja2Templates(
    directory=str(pathlib.Path(__file__).parent.absolute().joinpath("templates"))
)
