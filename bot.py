import discord
import json
from discord.ext import commands
from datetime import datetime

# Carregar configurações
with open("config.json", "r") as config_file:
    config = json.load(config_file)

TOKEN = config["TOKEN"]

# Configuração do bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.message_content = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)
log_channels = {}
cargo_updates = 0  # Contador de cargos atualizados

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    await ctx.send(f"✅ Canal de logs definido para {channel.mention}")

@bot.event
async def on_member_update(before, after):
    global cargo_updates
    if before.roles != after.roles:
        guild = after.guild
        log_channel_id = log_channels.get(guild.id)
        if not log_channel_id:
            return
        
        log_channel = bot.get_channel(log_channel_id)
        if not log_channel:
            return
        
        executor = None
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id:
                executor = entry.user
                break

        removed_roles = [role.name for role in before.roles if role not in after.roles]
        added_roles = [role.name for role in after.roles if role not in before.roles]
        timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        
        embed = discord.Embed(title="📌 **Atualização de Cargos**", color=0x3498db, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
        embed.add_field(name="👤 **Usuário Atualizado:**", value=f"{after.mention} ({after.id})", inline=False)
        embed.add_field(name="📅 **Data e Hora:**", value=f"{timestamp} UTC", inline=False)
        
        if executor:
            embed.add_field(name="⚙️ **Alterado Por:**", value=f"{executor.mention} ({executor.id})", inline=False)
        
        if added_roles:
            embed.add_field(name="🟢 **Cargos Adicionados:**", value=", ".join(added_roles), inline=False)
        if removed_roles:
            embed.add_field(name="🔴 **Cargos Removidos:**", value=", ".join(removed_roles), inline=False)
        
        embed.set_footer(text=f"Servidor: {guild.name}", icon_url=guild.icon.url if guild.icon else None)
        
        cargo_updates += 1  # Incrementar contador de cargos atualizados
        await log_channel.send(embed=embed)

@bot.command()
async def linix(ctx):
    await ctx.send(f"✅ Bot está online e funcionando! ({bot.user})")

@bot.command()
async def status(ctx):
    await ctx.send(f"📊 Total de cargos atualizados: {cargo_updates}")

bot.run(TOKEN)