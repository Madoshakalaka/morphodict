from django.db import models


class Word(models.Model):
    context = models.CharField(max_length=50)
    type = models.CharField(max_length=6)
    language = models.CharField(max_length=5)

    class Meta:
        select_on_save = True
        indexes = [
            models.Index(fields=["context"])
        ]


class Lemma(Word):
    pass

    class Meta:
        select_on_save = True


class Attribute(models.Model):
    name = models.CharField(max_length=10)
    fk_lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE)


class Inflection(Word):
    fk_lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE)

    class Meta:
        select_on_save = True


class InflectionForm(models.Model):
    name = models.CharField(max_length=10)
    fk_inflection = models.ForeignKey(Inflection, on_delete=models.CASCADE)

    class Meta:
        select_on_save = True


class Definition(models.Model):
    context = models.CharField(max_length=200)
    source = models.CharField(max_length=8)
    fk_word = models.ForeignKey(Word, on_delete=models.CASCADE)

    class Meta:
        select_on_save = True
