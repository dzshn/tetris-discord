import argparse
import pathlib
import webbrowser
from http.server import SimpleHTTPRequestHandler
from http.server import ThreadingHTTPServer

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=(
        'Properly serves docs/ for testing, letting vue-router handle pages.\n\n'
        'See https://next.router.vuejs.org/guide/essentials/history-mode.html#html5-mode for more info'
    ),
    usage='python docs.py [--port int]'
)
parser.add_argument('--port', default=8080, type=int, metavar='int')

args = parser.parse_args()


class DocsRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='docs/', **kwargs)

    def translate_path(self, path: str) -> str:
        path = super().translate_path(path)

        if not pathlib.Path(path).exists():
            return 'docs/index.html'

        return path


server = ThreadingHTTPServer(('0.0.0.0', args.port), DocsRequestHandler)

print(f'Serving docs/ on http://0.0.0.0:{args.port}/')
webbrowser.open(f'http://localhost:{args.port}')

try:
    server.serve_forever()

except KeyboardInterrupt:
    pass
