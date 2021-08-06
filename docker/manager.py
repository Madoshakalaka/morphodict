#!/usr/bin/env python3

"""
docker-compose management code

Intended to handle things like:
  - Generating docker-compose YAML files
  - Making sure directories exist
  - Creating database files
  - Triggering a migration run
  - Getting a shell into a running container

This is all together in one script so that the configuration is consistent: the
YAML files point at the right places because they are both created by code that
ultimately gets their location from the same variable.
"""
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from functools import cache
from pathlib import Path

from django.template import Template, Engine, Context

# Port assignments are tracked at:
# https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv
#
# If you want to run the Cypress tests on the staging container, use
# the following:
#
#     CYPRESS_BASE_URL=http://localhost:8001 npx cypress open
#
# See: https://docs.cypress.io/guides/guides/environment-variables.html#We-can-move-this-into-a-Cypress-environment-variable
APPS = {
    "crkeng": {"name": "itwewina", "port": 8011, "uwsgi_stats_port": 9191},
    "cwdeng": {"name": "itwiwina", "port": 8012, "uwsgi_stats_port": 9192},
    "srseng": {"name": "gunaha", "port": 8013, "uwsgi_stats_port": 9193},
    "arpeng": {"port": 8014, "uwsgi_stats_port": 9194},
}

DIR = Path(__file__).parent


class App:
    def __init__(self, language_pair, port, uwsgi_stats_port, name=None):
        self.language_pair = language_pair
        if name:
            self._name = name
        self.port = port
        self.uwsgi_stats_port = uwsgi_stats_port

    def lfs_mounts(self):
        """Large files that are mounted from the local git lfs checkout,
        instead of being built into the container."""
        return [
            "morphodict/lexicon/resources/vector_models/",
            f"{self.language_pair}/res/fst",
            # Holds phrase-translation FSTs
            "CreeDictionary/res/fst/",
        ]

    def prod_data_dir(self):
        return f"/data_local/application-data/{self.name}"

    def data_mounts(self):
        return [
            DataMount(self, "resources/vector_models/"),
            DataMount(self, "db/"),
            DataMount(self, "CreeDictionary/search_quality"),
        ]

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        return self.language_pair


class DataMount:
    def __init__(self, app, path):
        self.app = app
        self._path = path

        self.target = f"/app/src/{app.language_pair}/{path}"
        self.dev_src = f"../src/{app.language_pair}/{path}"

    @property
    def prod_src(self):
        """Where to mount this path from in prod.

        Defaults to a subfolder in app.prod_data_dir(), using only the last
        directory component of the target path.
        """
        # The gymnastics are to preserve trailing slashes
        if self._path.endswith("/"):
            basename = os.path.basename(os.path.dirname(self._path))
        else:
            basename = os.path.basename(self._path)

        return f"{self.app.prod_data_dir()}/{basename}"


@cache
def build_dictionary_info():
    return [App(k, **v) for k, v in APPS.items()]


@cache
def get_engine():

    # Raise an error if a template refers to a nonexistent variable. Inspired by
    # https://stackoverflow.com/a/15312316/14558
    class InvalidVariableReference:
        """
        A reference to an invalid variable, arising from a Django template.
        Raises an exception when used.
        """

        def _error_out(self):
            raise Exception("this should not get called")

        def __contains__(self, item):
            if item == "%s":
                return True
            self._error_out()

        def __mod__(self, other):
            raise Exception(f"Invalid variable access: {other!r}")

        def __getattr__(self, item):
            self._error_out()

    return Engine(string_if_invalid=InvalidVariableReference())


def render_template(template_string, context_dict):
    template = Template(template_string, engine=get_engine())
    context = Context(context_dict, use_l10n=False)
    return template.render(context)


def clean_up_whitespace_in_template_output(text):
    """Remove some excess whitespace from using Django templates for YAML."""

    ret = []
    for line in text.split("\n"):
        # Truly empty lines are likely intentional, so keep them
        if not line:
            ret.append("")
            continue

        # If the line consists entirely of trailing whitespace, it is likely an
        # artifact of template tag formatting, so drop it.
        line = line.rstrip()
        if not line:
            continue

        ret.append(line)

    text = "\n".join(ret)
    if not text.endswith("\n"):
        text += "\n"
    return text


def make_yaml(args):
    context = {
        "autogeneration_notice": "# WARNING: This file is autogenerated. Edit the .template file instead.",
        "apps": build_dictionary_info(),
    }

    for path in ["docker-compose.yml", "docker-compose.staging-override-sample.yml"]:
        filled = render_template((DIR / (path + ".template")).read_text(), context)

        filled = clean_up_whitespace_in_template_output(filled)

        out_file = DIR / path
        out_file.write_text(filled)

        print(f"Wrote {out_file}")


def main():
    parser = ArgumentParser()
    parser.formatter_class = ArgumentDefaultsHelpFormatter

    subparsers = parser.add_subparsers()
    make_yaml_parser = subparsers.add_parser(
        "make-yaml", help="Create the various docker-compose*.yml files"
    )

    make_yaml_parser.set_defaults(func=make_yaml)

    args = parser.parse_args()

    if "func" not in args:
        parser.error("No command specified")
    args.func(args)


if __name__ == "__main__":
    main()
