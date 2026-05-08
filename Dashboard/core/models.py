from django.db import models

class GuildConfig(models.Model):
    guild_id = models.CharField(max_length=100, primary_key=True)
    mod_role_ids = models.TextField(blank=True, null=True)
    ticket_role_ids = models.TextField(blank=True, null=True)
    welcome_channel_id = models.CharField(max_length=100, blank=True, null=True)
    j2c_lobby_channel_id = models.CharField(max_length=100, blank=True, null=True)
    j2c_category_channel_id = models.CharField(max_length=100, blank=True, null=True)
    ticket_embed_channel_id = models.CharField(max_length=100, blank=True, null=True)
    ticket_category_id = models.CharField(max_length=100, blank=True, null=True)

    use_bot_db = True  # Custom attribute for router

    class Meta:
        managed = False
        db_table = 'guild_config'

    def __str__(self):
        return f"Guild {self.guild_id}"
