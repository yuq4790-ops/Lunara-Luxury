import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import io
from datetime import datetime
from dotenv import load_dotenv


TOKEN = os.getenv("TOKEN")

GUILD_ID = 1552013736070357132

TICKET_CATEGORY_ID = 1552053294644469842

SUPPORT_ROLE_ID = 1552047129588142201

TRANSCRIPT_CHANNEL_ID = 1552846873394675742

VOICE_CHANNEL_ID = 1553116493905133669


intents = discord.Intents.default()

intents.members = True
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)




class TicketBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            status=discord.Status.online,
            activity=discord.Streaming(
                name="Lunara Luxury",
                url="https://www.twitch.tv/discord"
            )
        )




    async def setup_hook(self):

        # Register persistent Views
        self.add_view(TicketPanel())
        self.add_view(TicketView())

        # Sync slash commands to the configured server
        guild = discord.Object(id=GUILD_ID)

        self.tree.copy_global_to(guild=guild)

        await self.tree.sync(guild=guild)


bot = TicketBot()



def create_ticket_topic(
    owner_id: int,
    claimed_id: int | None = None,
    ticket_type: str = "support"
):

    if claimed_id is None:
        claimed = "none"
    else:
        claimed = str(claimed_id)

    return (
        f"ticket_owner={owner_id};"
        f"ticket_claimed={claimed};"
        f"ticket_type={ticket_type}"
    )


def get_ticket_data(
    channel: discord.TextChannel
):

    if not channel.topic:
        return None

    if not channel.topic.startswith(
        "ticket_owner="
    ):
        return None

    try:

        parts = channel.topic.split(";")

        owner_id = int(
            parts[0].split("=")[1]
        )

        claimed_value = (
            parts[1]
            .split("=")[1]
        )

        if claimed_value == "none":
            claimed_id = None
        else:
            claimed_id = int(
                claimed_value
            )

        ticket_type = "support"
        for part in parts[2:]:
            if part.startswith("ticket_type="):
                ticket_type = part.split("=", 1)[1]
                break

        return {
            "owner_id": owner_id,
            "claimed_id": claimed_id,
            "ticket_type": ticket_type
        }

    except (ValueError, IndexError):

        return None


def find_user_ticket(
    guild: discord.Guild,
    user_id: int
):

    for channel in guild.text_channels:

        ticket = get_ticket_data(channel)

        if ticket is None:
            continue

        if ticket["owner_id"] == user_id:
            return channel

    return None


def is_support(
    member: discord.Member
):

    return any(
        role.id == SUPPORT_ROLE_ID
        for role in member.roles
    )



async def create_transcript(
    channel: discord.TextChannel
):

    ticket = get_ticket_data(channel)

    if ticket is None:
        return None

    owner_id = ticket["owner_id"]
    claimed_id = ticket["claimed_id"]
    ticket_type = ticket.get("ticket_type", "support")

    lines = []


    lines.append(
        "DISCORD TICKET TRANSCRIPT"
    )


    lines.append(
        f"Server: {channel.guild.name}"
    )

    lines.append(
        f"Channel: #{channel.name}"
    )

    lines.append(
        f"Channel ID: {channel.id}"
    )

    lines.append(
        f"Ticket Owner ID: {owner_id}"
    )

    lines.append(
        f"Ticket Type: {ticket_type.capitalize()}"
    )

    if claimed_id:

        lines.append(
            f"Claimed By ID: {claimed_id}"
        )

    else:

        lines.append(
            "Claimed By: Nobody"
        )

    lines.append(
        "Created: "
        + channel.created_at.strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    )

    lines.append(
        "Transcript Created: "
        + datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    )

    lines.append("")


    lines.append(
        "MESSAGES"
    )


    lines.append("")

    async for message in channel.history(
        limit=None,
        oldest_first=True
    ):

        timestamp = message.created_at.strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        lines.append(
            f"[{timestamp}] "
            f"{message.author} "
            f"({message.author.id})"
        )

        if message.content:

            lines.append(
                message.content
            )

        for attachment in message.attachments:

            lines.append(
                f"[Attachment] {attachment.filename}"
            )

            lines.append(
                f"[URL] {attachment.url}"
            )

        if message.embeds:

            lines.append(
                f"[{len(message.embeds)} Embed(s)]"
            )

        lines.append("")

        lines.append(
            "-" * 60
        )

        lines.append("")

    transcript = "\n".join(lines)

    return io.BytesIO(
        transcript.encode("utf-8")
    )


class TicketPanel(discord.ui.LayoutView):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        container = discord.ui.Container()

        container.add_item(
            discord.ui.TextDisplay(
                "# Support Ticket"
            )
        )



        container.add_item(
            discord.ui.TextDisplay(
                "- **Need help?**\n\n"
                "> Were here to assist you!\n"
                "> Whether youre looking for a specific item,\n "
                "> have a question about an order or need help\n "
                "> with anything else our team is ready to help.\n\n"
                "- **Please provide as much information as possible!**\n\n "
                "> so we can handle your request quickly and efficiently.\n"
                "> Click **Create Ticket** below to open a private\n "
                "> support ticket with our team."
            )
        )
        container.add_item(
            discord.ui.Separator()
        )
        container.add_item(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://media.discordapp.net/attachments/1366037520831483975/1552417495707689070/Design_ohne_Titel_4.png"
                )
            )
        )
        container.add_item(
            discord.ui.Separator()
        )

        row = discord.ui.ActionRow()

        row.add_item(
            discord.ui.Button(
                label="Support",
                style=discord.ButtonStyle.blurple,
                custom_id="ticket_support"
            )
        )

        row.add_item(
            discord.ui.Button(
                label="Buy",
                style=discord.ButtonStyle.success,
                custom_id="ticket_buy"
            )
        )

        row.add_item(
            discord.ui.Button(
                label="Application",
                style=discord.ButtonStyle.secondary,
                custom_id="ticket_application"
            )
        )

        container.add_item(row)

        self.add_item(container)




class TicketView(discord.ui.LayoutView):

    def __init__(
        self,
        owner_mention: str = "the ticket owner",
        ticket_type: str = "support"
    ):

        super().__init__(
            timeout=None
        )

        container = discord.ui.Container()

        ticket_titles = {
            "support": "Support Ticket",
            "buy": "Buy Ticket",
            "application": "Team Application"
        }

        ticket_descriptions = {
            "support": (
                "> Please describe your issue in as much detail as possible."
            ),
            "buy": (
                "> Please tell us what you want to buy and provide all relevant details."
            ),
            "application": (
                "> Thanks for your interest in joining our team! "
                "Please provide the requested application information."
            )
        }

        ticket_title = ticket_titles.get(ticket_type, "Support Ticket")
        ticket_description = ticket_descriptions.get(
            ticket_type,
            ticket_descriptions["support"]
        )

        accessory = discord.ui.Thumbnail(
            media="https://media.discordapp.net/attachments/1366037520831483975/1552417495707689070/Design_ohne_Titel_4.png"
        )

        section = discord.ui.Section(
            discord.ui.TextDisplay(
                f"# Lunara Luxury — {ticket_title}"
            ),
            discord.ui.TextDisplay(
                f"{owner_mention}.\n\n"
                f"{ticket_description}\n\n"
                "> The support team can claim the ticket.\n"
                "> Dont mass ping our Staff or you will be muted for 24h!\n"
            ),
            accessory=accessory
        )

        container.add_item(section)

        container.add_item(
            discord.ui.Separator()
        )

        row = discord.ui.ActionRow()

        row.add_item(
            discord.ui.Button(
                label="Claim",
                style=discord.ButtonStyle.success,
                custom_id="ticket_claim"
            )
        )

        row.add_item(
            discord.ui.Button(
                label="Transcript",
                style=discord.ButtonStyle.secondary,
                custom_id="ticket_transcript"
            )
        )

        row.add_item(
            discord.ui.Button(
                label="Close",
                style=discord.ButtonStyle.danger,
                custom_id="ticket_close"
            )
        )

        container.add_item(row)

        self.add_item(container)



@bot.listen("on_interaction")
async def ticket_interaction(
    interaction: discord.Interaction
):

    if interaction.type != discord.InteractionType.component:
        return

    if interaction.guild is None:
        return

    if interaction.data is None:
        return

    custom_id = interaction.data.get(
        "custom_id"
    )

    if custom_id is None:
        return

    guild = interaction.guild


    ticket_type_map = {
        "ticket_support": "support",
        "ticket_buy": "buy",
        "ticket_application": "application"
    }

    if custom_id in ticket_type_map:

        ticket_type = ticket_type_map[custom_id]

        existing_ticket = find_user_ticket(
            guild,
            interaction.user.id
        )

        if existing_ticket:

            await interaction.response.send_message(
                f"You already have an open ticket: "
                f"{existing_ticket.mention}",
                ephemeral=True
            )

            return

        category = guild.get_channel(
            TICKET_CATEGORY_ID
        )

        if not isinstance(
            category,
            discord.CategoryChannel
        ):

            await interaction.response.send_message(
                "The configured ticket category "
                "could not be found.",
                ephemeral=True
            )

            return

        support_role = guild.get_role(
            SUPPORT_ROLE_ID
        )

        if support_role is None:

            await interaction.response.send_message(
                "The configured support role "
                "could not be found.",
                ephemeral=True
            )

            return

        bot_member = guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "The bot member could not be found.",
                ephemeral=True
            )

            return

        # Channel permissions
        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),

            support_role:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),

            bot_member:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True,
                    manage_channels=True,
                    manage_messages=True
                )
        }

        # Create channel
        channel = await guild.create_text_channel(

            name=f"{ticket_type}-{interaction.user.name}",

            category=category,

            overwrites=overwrites,

            topic=create_ticket_topic(
                interaction.user.id,
                ticket_type=ticket_type
            ),

            reason=(
                f"{ticket_type.capitalize()} ticket created by "
                f"{interaction.user}"
            )
        )

        await interaction.response.send_message(
            f"Your ticket has been created: "
            f"{channel.mention}",
            ephemeral=True
        )

        await channel.send(
            view=TicketView(
                owner_mention=interaction.user.mention,
                ticket_type=ticket_type
            )
        )

        return


    channel = interaction.channel

    if not isinstance(
        channel,
        discord.TextChannel
    ):
        return

    ticket = get_ticket_data(channel)

    if ticket is None:
        return

    owner_id = ticket["owner_id"]
    claimed_id = ticket["claimed_id"]


    if custom_id == "ticket_claim":

        if not isinstance(
            interaction.user,
            discord.Member
        ):
            return

        if not is_support(
            interaction.user
        ):

            await interaction.response.send_message(
                "Only members with the support role "
                "can claim tickets.",
                ephemeral=True
            )

            return

        if claimed_id is not None:

            await interaction.response.send_message(
                f"This ticket has already been claimed "
                f"by <@{claimed_id}>.",
                ephemeral=True
            )

            return

        await channel.edit(
            topic=create_ticket_topic(
                owner_id,
                interaction.user.id,
                ticket.get("ticket_type", "support")
            )
        )

        await interaction.response.send_message(
            f"{interaction.user.mention} "
            "has claimed this ticket."
        )

        return


    if custom_id == "ticket_transcript":

        if not isinstance(
            interaction.user,
            discord.Member
        ):
            return

        if (
            interaction.user.id != owner_id
            and not is_support(
                interaction.user
            )
        ):

            await interaction.response.send_message(
                "You are not allowed to create "
                "a transcript for this ticket.",
                ephemeral=True
            )

            return

        await interaction.response.defer(
            ephemeral=True
        )

        transcript = await create_transcript(
            channel
        )

        if transcript is None:

            await interaction.followup.send(
                "Failed to create the transcript.",
                ephemeral=True
            )

            return

        file = discord.File(
            transcript,
            filename=f"transcript-{channel.id}.txt"
        )

        await interaction.followup.send(
            "Here is the ticket transcript.",
            file=file,
            ephemeral=True
        )

        return


    if custom_id == "ticket_close":

        if not isinstance(
            interaction.user,
            discord.Member
        ):
            return

        if (
            interaction.user.id != owner_id
            and not is_support(
                interaction.user
            )
        ):

            await interaction.response.send_message(
                "You are not allowed to close "
                "this ticket.",
                ephemeral=True
            )

            return

        await interaction.response.defer()


        transcript = await create_transcript(
            channel
        )


        transcript_channel = guild.get_channel(
            TRANSCRIPT_CHANNEL_ID
        )

        if (
            isinstance(
                transcript_channel,
                discord.TextChannel
            )
            and transcript is not None
        ):

            file = discord.File(
                transcript,
                filename=f"transcript-{channel.id}.txt"
            )

            claimed_text = (
                f"<@{claimed_id}>"
                if claimed_id
                else "Nobody"
            )

            await transcript_channel.send(
                content=(
                    "Ticket Closed\n\n"
                    f"Ticket: `{channel.name}`\n"
                    f"Ticket Owner: <@{owner_id}>\n"
                    f"Ticket Type: {ticket.get('ticket_type', 'support').capitalize()}\n"
                    f"Closed By: {interaction.user.mention}\n"
                    f"Claimed By: {claimed_text}"
                ),
                file=file
            )


        await channel.delete(
            reason=(
                f"Ticket closed by "
                f"{interaction.user}"
            )
        )



@bot.tree.command(
    name="ticketpanel",
    description="Send the ticket panel"
)
@app_commands.guilds(
    discord.Object(id=GUILD_ID)
)
async def ticketpanel(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "You need administrator permissions "
            "to use this command.",
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        view=TicketPanel()
    )

    async def reconnect_voice(guild):
        global reconnect_task

        await asyncio.sleep(3)

        channel = guild.get_channel(VOICE_CHANNEL_ID)

        if channel is None:
            print("Voice channel not found.")
            reconnect_task = None
            return

        for attempt in range(1, 6):
            try:
                voice_client = guild.voice_client

                if voice_client is not None and voice_client.is_connected():
                    if voice_client.channel.id == VOICE_CHANNEL_ID:
                        print("Bot is already connected to the correct voice channel.")
                        reconnect_task = None
                        return

                    await voice_client.disconnect(force=True)
                    await asyncio.sleep(2)

                print(f"Voice reconnect attempt {attempt}/5...")

                await channel.connect(
                    reconnect=True
                )

                print(f"Bot reconnected to: {channel.name}")
                reconnect_task = None
                return

            except Exception as e:
                print(f"Voice reconnect attempt {attempt} failed: {e}")

                if attempt < 5:
                    await asyncio.sleep(5)

        print("Voice reconnect failed after 5 attempts.")
        reconnect_task = None

    @bot.event
    async def on_voice_state_update(member, before, after):

        global reconnect_task

        if member.id != bot.user.id:
            return

        print(
            f"Bot voice state changed: "
            f"before={before.channel}, after={after.channel}"
        )

        if after.channel is not None:
            if after.channel.id == VOICE_CHANNEL_ID:
                print("Bot is in the correct voice channel.")
                return

        print("Bot is not in the configured voice channel.")

        if reconnect_task is not None and not reconnect_task.done():
            print("Voice reconnect is already running.")
            return

        reconnect_task = asyncio.create_task(
            reconnect_voice(member.guild)
        )



TRUSTED_ROLE_ID = 1240934720095653909

@bot.event
async def on_webhooks_update(channel: discord.abc.GuildChannel):
    guild = channel.guild

    webhooks = await guild.webhooks()

    for webhook in webhooks:
        if webhook.channel_id != channel.id:
            continue

        if webhook.user is None:
            continue

        member = guild.get_member(webhook.user.id)
        if member is None:
            continue

        if all(role.id != TRUSTED_ROLE_ID for role in member.roles):
            try:
                await webhook.delete(reason="Webhook forbidden")
                print(f"Webhook from {member} deleted.")
            except discord.Forbidden:
                print("No perms to delete Webhook.")





@bot.event
async def on_ready():
    print("=" * 50)
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("=" * 50)

    guild = bot.get_guild(GUILD_ID)

    if guild is None:
        print("Guild not found.")
        return

    print(f"Guild found: {guild.name}")

    channel = guild.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        print("Voice channel not found.")
        return

    print(f"Voice channel found: {channel.name}")

    try:
        voice_client = guild.voice_client

        if voice_client is None:
            await channel.connect(reconnect=True)
            print(f"Connected to: {channel.name}")

        elif voice_client.channel.id != channel.id:
            await voice_client.move_to(channel)
            print(f"Moved to: {channel.name}")

        else:
            print("Bot is already in the correct voice channel.")

    except discord.Forbidden:
        print("Discord denied the voice connection.")

    except Exception as e:
        print(f"Voice connection error: {e}")

    print("Anti-Webhook protection enabled.")




bot.run(TOKEN)
