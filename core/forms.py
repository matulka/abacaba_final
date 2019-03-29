from django import forms

class SearchForm(forms.Form):
    input = forms.CharField(label='Поиск',
                            min_length=1,
                            max_length=100,
                            empty_value='Продукция abacaba')
