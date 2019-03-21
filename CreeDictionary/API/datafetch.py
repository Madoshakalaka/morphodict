from API.models import *
from django.forms.models import model_to_dict
from django.db.models.functions import Length


# Exact Lemma
def fetchExactLemma(lemma):
    lemmas = Lemma.objects.filter(context__exact=lemma)
    return lemmas


def fetchContainsLemma(lemma):
    lemmas = Lemma.objects.filter(context__contains=lemma)
    return lemmas


def fetchLemmaContainsInflection(inflection):
    lemmaIDs = Inflection.objects.filter(context__contains=inflection).values_list("fk_lemma_id", flat=True)
    lemmas = Lemma.objects.filter(word_ptr_id__in=lemmaIDs)
    return lemmas


def fetchLemmaContainsDefinition(definition):
    lemmas = list()
    wordIDs = Definition.objects.filter(
        context__contains=definition).extra(
        select={
            'length': 'Length(context)'}).order_by('length').values_list(
                "fk_word_id", flat=True)
    lemmaResult = Lemma.objects.filter(word_ptr_id__in=wordIDs)

    # Sort Lemma Based on Definition Order
    for wordID in wordIDs:
        for lemma in lemmaResult:
            if wordID == lemma.id:
                lemmas.append(lemma)
                break

    lemmaIDs = Inflection.objects.filter(word_ptr_id__in=wordIDs).values_list("fk_lemma_id", flat=True)
    lemmas += Lemma.objects.filter(word_ptr_id__in=lemmaIDs)

    print(list(lemmas))
    return lemmas


def fillDefinitions(words):
    """
        Args:
            words (list<dict>): List of words in dictionary form
    """
    for word in words:
        definitions = Definition.objects.filter(fk_word_id=int(word["id"]))
        definitions = list(model_to_dict(definition) for definition in definitions)
        word["definitions"] = definitions


def fillAttributes(words):
    """
    Args:
        words (list<dict>): List of words in dictionary form
    """
    for word in words:
        attributes = Attribute.objects.filter(fk_lemma_id=int(word["id"]))
        attributes = list(model_to_dict(attribute) for attribute in attributes)
        word["attributes"] = attributes
