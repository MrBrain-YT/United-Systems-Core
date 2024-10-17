import logging

import click

# Seting up flask logging
def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass
def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass
click.echo = echo
click.secho = secho
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)