from django import forms
from .models import GuildConfig

class GuildConfigForm(forms.ModelForm):
    class Meta:
        model = GuildConfig
        fields = [
            'guild_id', 'mod_role_ids', 'ticket_role_ids', 
            'welcome_channel_id', 'j2c_lobby_channel_id', 
            'j2c_category_channel_id', 'ticket_embed_channel_id', 
            'ticket_category_id'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
