# adding from git

import discord
from discord.ext import commands
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def google_authenticate():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


def create_event(creds, event_details):
    service = build("calendar", "v3", credentials=creds)
    event = {
        "summary": event_details["summary"],
        "start": {
            "dateTime": event_details["start"],
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": event_details["end"],
            "timeZone": "America/Los_Angeles",
        },
        "attendees": [{"email": email} for email in event_details["attendees"]],
    }
    event = service.events().insert(calendarId="primary", body=event).execute()
    return event.get("htmlLink")


@bot.command()
async def schedule(ctx, summary: str, start: str, end: str):
    attendees = [member.name + "@example.com" for member in ctx.guild.members]

    creds = google_authenticate()
    event_details = {
        "summary": summary,
        "start": start,
        "end": end,
        "attendees": attendees,
    }
    meeting_link = create_event(creds, event_details)

    await ctx.send(f"Meeting scheduled! Join here: {meeting_link}")


bot.run("Your discord bot token")
