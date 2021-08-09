"""
Convenience functions for using Django’s template system outside of a
traditional Django app.
"""

from functools import cache

from django.template import Engine, Template, Context


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
