from jinja2 import nodes
from jinja2.ext import Extension

import sheerlike.middleware

from .utils import hash_for_script


class CSPScriptHashExtension(Extension):
    tags = {'hashedscript'}

    def parse(self, parser):

        # don't know if this is actually neccessary:
        lineno = next(parser.stream).lineno

        body = parser.parse_statements(['name:end_hashedscript'],
                                       drop_needle=True)

        return nodes.CallBlock(self.call_method('_hash_script'),

                               [], [], body).set_lineno(lineno)

    def _hash_script(self, caller):
        js = caller()
        request = sheerlike.middleware.get_request()
        if not hasattr(request, 'script_hashes'):
            request.script_hashes = []
        hash = hash_for_script(js)
        request.script_hashes.append(hash)
        return "<script>{js}</script>".format(js=js)

#: nicer import name
csp = CSPScriptHashExtension
