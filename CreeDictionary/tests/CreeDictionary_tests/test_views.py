import logging
from typing import Dict, Optional

import pytest
from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.test import Client
from django.urls import reverse


@pytest.fixture(scope="module")
def django_db_setup():
    """
    This works with pytest-django plugin.
    This fixture tells all functions marked with pytest.mark.django_db in this file
    to use the database specified in settings.py
    which is the existing test_db.sqlite3 if USE_TEST_DB=True is passed.

    Instead of by default, an empty database in memory.
    """

    # all functions in this file should use the existing test_db.sqlite3
    assert settings.USE_TEST_DB


class TestLemmaDetailsInternal4xx:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("lemma_id", "paradigm_size", "expected_code"),
        [
            ["-10", "FULL", HttpResponseBadRequest.status_code],
            ["10", None, HttpResponseBadRequest.status_code],
            ["5.2", "LINGUISTIC", HttpResponseBadRequest.status_code],
            ["123", "LINUST", HttpResponseBadRequest.status_code],
            [
                "99999999",
                "FULL",
                HttpResponseNotFound.status_code,
            ],  # we'll never have as many as 99999999 entries in the database so it's a non-existent id
        ],
    )
    def test_paradigm_details_internal_400_404(
        self, lemma_id: Optional[str], paradigm_size: Optional[str], expected_code: int
    ):
        c = Client()

        get_data: Dict[str, str] = {}
        if lemma_id is not None:
            get_data["lemma-id"] = lemma_id
        if paradigm_size is not None:
            get_data["paradigm-size"] = paradigm_size
        response = c.get(reverse("cree-dictionary-paradigm-detail"), get_data)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(("method",), (("post",), ("put",), ("delete",)))
    def test_paradigm_details_internal_wrong_method(self, method: str):
        c = Client()
        response = getattr(c, method)(
            reverse("cree-dictionary-paradigm-detail"),
            {"lemma-id": 1, "paradigm-size": "BASIC"},
        )
        assert response.status_code == HttpResponseNotAllowed.status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        reverse("cree-dictionary-index"),
        reverse("cree-dictionary-search") + "?q=kotiskâwêw",
        reverse("cree-dictionary-about"),
        reverse("cree-dictionary-contact-us"),
        # Note: do NOT test word-detail page, as this page has tonnes of "errors"
        # checking for things like is_title, is_label, is_heading, etc.
    ],
)
def test_pages_render_without_template_errors(url: str, client: Client, caplog):
    """
    Ensure the index page renders without template errors.

    Note: template errors are not necessarily errors, but Django logs them anyway 🙃
    See: https://docs.djangoproject.com/en/3.1/ref/templates/api/#how-invalid-variables-are-handled
    """
    with caplog.at_level(logging.DEBUG):
        req = client.get(url)

    assert req.status_code == 200

    template_errors = [log for log in caplog.records if is_template_error(log)]
    assert len(template_errors) == 0


def is_template_error(record: logging.LogRecord) -> bool:
    """
    Looking for an error log that looks like this:

        Exception while resolving variable 'X' in template 'Y'.
        Traceback (most recent call last):
            ...
        SomeError: error

    """
    if record.name != "django.template":
        return False

    if not record.exc_info:
        return False

    return True
