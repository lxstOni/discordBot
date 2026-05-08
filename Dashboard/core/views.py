from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import GuildConfig
from .forms import GuildConfigForm

@login_required
def dashboard_home(request):
    configs = GuildConfig.objects.all()
    return render(request, 'core/home.html', {'configs': configs})

@login_required
def edit_guild_config(request, guild_id):
    config, created = GuildConfig.objects.get_or_create(guild_id=guild_id)
    
    if request.method == 'POST':
        form = GuildConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('dashboard_home')
    else:
        form = GuildConfigForm(instance=config)

    return render(request, 'core/edit_config.html', {'form': form, 'guild_id': guild_id})
