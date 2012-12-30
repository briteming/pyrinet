import wtforms as forms
v = forms.validators


class AddForm(forms.Form):
    protocol = forms.TextField(validators=[v.AnyOf(['tcp', 'udp'])])
    local_ip = forms.TextField(validators=[v.IPAddress()])
    local_port = forms.IntegerField(validators=[v.NumberRange(min=10, max=65535)])
    remote_ip = forms.TextField(validators=[v.IPAddress()])
    remote_port = forms.IntegerField(validators=[v.NumberRange(min=10, max=65535)])
