from django import forms


class AdminUUIDInputWidget(forms.TextInput):
    def __init__(self, attrs=None):
        super().__init__(attrs={'class': 'vUUIDField', **(attrs or {})})
