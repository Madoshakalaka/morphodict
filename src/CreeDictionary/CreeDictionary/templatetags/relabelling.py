"""
Access to relabelling from templates.
"""

import logging
from typing import Sequence

from django import template
from django.template import Context

from CreeDictionary.CreeDictionary.relabelling import read_labels
from CreeDictionary.morphodict.templatetags.morphodict_orth import orth_tag
from CreeDictionary.utils.types import FSTTag
from crkeng.app.preferences import ParadigmLabel

logger = logging.getLogger(__name__)
register = template.Library()

# If a paradigm label preference is not set, use this one!
DEFAULT_PARADIGM_LABEL = "english"


def label_setting_to_relabeller(label_setting: str):
    labels = read_labels()
    return {
        "english": labels.english,
        "linguistic": labels.linguistic_short,
        "nehiyawewin": labels.cree,
    }[label_setting]


@register.simple_tag(takes_context=True)
def relabel(context: Context, tags: Sequence[FSTTag], labels=None):
    """
    Gets the best matching label for the given object.
    """

    if labels is None:
        label_setting = label_setting_from_context(context)
    else:
        label_setting = labels

    relabeller = label_setting_to_relabeller(label_setting)

    if label := relabeller.get_longest(tags):
        if label_setting == "nehiyawewin":
            return orth_tag(context, label)
        return label

    logger.warning("Could not find relabelling for tags: %r", tags)
    return "+".join(tags)


@register.simple_tag(takes_context=True)
def relabel_one(context: Context, tag: FSTTag, **kwargs):
    """
    Relabels exactly one tag (a string). I use this instead of widening the type on
    relabel() because polymorphic arguments make me nervous 😬
    """
    return relabel(context, (tag,), **kwargs)


@register.simple_tag(takes_context=True)
def relabel_based_on_display_mode(context: Context, tag: FSTTag, **kwargs):
    """
    Relabels exactly one tag (a string). I use this instead of widening the type on
    relabel() because polymorphic arguments make me nervous 😬
    """
    return relabel(
        context, (tag,), labels=label_setting_from_display_mode(context), **kwargs
    )


def label_setting_from_context(context: Context):
    """
    Returns the most appropriate paradigm label preference.
    :param context: a simple template Context or a RequestContext
    """
    if hasattr(context, "request"):
        # We can get the paradigm label from the cookie!
        return context.request.COOKIES.get(
            ParadigmLabel.cookie_name, ParadigmLabel.default
        )

    # Cannot get the request context? We can't detect the current cookie :/
    return ParadigmLabel.default


def label_setting_from_display_mode(context: Context):
    """
    Maps from the DisplayMode preference to the appropriate relabelling (see crkeng.preferences).
    """
    mode = context["preferences"].display_mode.current_choice
    if mode == "linguistic":
        return "linguistic"
    elif mode == "community":
        return "english"
    else:
        raise NotImplementedError(f"I don't know what to do for display mode: {mode}")
