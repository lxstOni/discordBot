import discord
from discord.ext import commands
from discord import File
from discord.utils import get
from easy_pil import Editor, load_image_async, Font
import ezcord
import os
from source.paths import get_welcome_image_path


class Welcome(ezcord.Cog, emoji="👋", description="Welcome System - Begrüße neue Member"):
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        image_path = get_welcome_image_path()

        pos = sum(m.joined_at < member.joined_at for m in member.guild.members if m.joined_at is not None)

        if pos == 1:
            te = "st"
        elif pos == 2:
            te = "nd"
        elif pos == 3:
            te = "rd"
        else:
            te = "th"

        background = Editor(image_path)
        profile_image = await load_image_async(str(member.display_avatar.url))

        profile = Editor(profile_image).resize((150, 150)).circle_image()
        poppins = Font.poppins(size=40, variant="bold")

        poppins_small = Font.poppins(size=25, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="gold", stroke_width=4)

        background.text((400, 260), f"WELCOME TO {member.guild.name}", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.display_name}", color="red", font=poppins_small,
                        align="center")
        background.text((400, 360), f"You Are The {pos}{te} Member", color="red", font=poppins_small,
                        align="center")

        file = File(fp=background.image_bytes, filename=image_path)

        await channel.send(
            f"Heya {member.mention}! Welcome To **{member.guild.name}**. For More Information Go To <#885152158599770183>.")
        await channel.send(file=file)


def setup(bot):
    bot.add_cog(Welcome(bot))