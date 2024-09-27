from PrimatesGameAPI.models import RPiBoards , Primates , Games , Reports
from django import forms 
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML



class PrimatesForm(forms.Form):
    name = forms.CharField(max_length=255)
    
    

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username','first_name','last_name','email']
        
        
def validate_choice(value):
    if not(isinstance(value, int)):
        raise forms.ValidationError('Invalid choice selected')
    
class StartGameForm(forms.Form):
    def __init__(self, *args, **kwargs):
        rpi_name_list = RPiBoards.objects.filter(rpistates__is_occupied=False)  # Only include not occupied boards
        primate_name_list = Primates.objects.all()
        game_name_list = Games.objects.all()
        report_list = Reports.objects.all()
        
        rpi_choices = [(int(obj.pk), obj.board_name) for obj in rpi_name_list]
        primate_choices = [(int(obj.pk),  obj.name) for obj in primate_name_list]
        game_choices = [(int(obj.pk), obj.name) for obj in game_name_list]
        report_choices = [(int(obj.pk), obj.reportname) for obj in report_list]
        
        super(StartGameForm, self).__init__(*args, **kwargs)
        if rpi_name_list and primate_name_list and game_name_list and report_list:
            self.fields['rpi_name'] = forms.ChoiceField(choices=rpi_choices)
            self.fields['primate_name'] = forms.ChoiceField(choices=primate_choices)
            self.fields['game_name'] = forms.ChoiceField(choices=game_choices)
            self.fields['report_name'] = forms.ChoiceField(choices=report_choices)
            
            
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<select name="my_field" class="form-control">'),
            *[(int(pk), str(choice)) for pk, choice in game_choices],
            *[(int(pk), str(choice)) for pk, choice in rpi_choices],
            *[(int(pk), str(choice)) for pk, choice in primate_choices],
            *[(int(pk), str(choice)) for pk, choice in report_choices],
            HTML('</select>'),
            Submit('submit', 'Submit', css_class='btn btn-primary')
        )
    game_name = forms.ChoiceField(validators=[validate_choice])
    rpi_name = forms.ChoiceField( validators=[validate_choice])
    primate_name  = forms.ChoiceField(validators=[validate_choice])
    report_name = forms.ChoiceField(validators=[validate_choice])
    
    