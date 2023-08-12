from django import forms


class URLCheckForm(forms.Form):
    url = forms.URLField(required=True)
    type = forms.ChoiceField(required=True, choices=(('db', 'A'), ('good_reads', 'B')))
    kind = forms.ChoiceField(required=True, choices=(('book', 'A'), ('author', 'B')))


class BookEditonURLImportForm(forms.Form):
    url = forms.URLField(required=True, label="URL")
    type = forms.ChoiceField(required=True, label="Source", choices=(('normal', 'A'), ('good_reads', 'B')))
    lang = forms.CharField(required=True, label="Language")
    book_id = forms.IntegerField(required=True, label="Book ID")


class BookSearchParamForm(forms.Form):
    author_name = forms.CharField(required=False, max_length=256)
    book_name = forms.CharField(required=False, max_length=256)
    series_name = forms.CharField(required=False, max_length=256)
