#!/usr/bin/env python3
"""
Word of the Day SMS Service

Fetches Merriam-Webster's word of the day and sends it via SMS
using an email-to-SMS gateway.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
import feedparser
import re
from html import unescape


def get_word_of_the_day():
    """Fetch the word of the day from Merriam-Webster's RSS feed."""
    feed_url = "https://www.merriam-webster.com/wotd/feed/rss2"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        raise Exception("No entries found in RSS feed")
    
    entry = feed.entries[0]
    
    # The title contains the word
    word = entry.title.strip()
    
    # Parse the description for definition and example
    description = entry.description
    
    # Clean HTML tags and decode entities
    clean_desc = re.sub(r'<[^>]+>', '', description)
    clean_desc = unescape(clean_desc)
    
    # Extract part of speech and definition
    # Format is typically: "part of speech : definition"
    lines = [line.strip() for line in clean_desc.split('\n') if line.strip()]
    
    definition = ""
    example = ""
    part_of_speech = ""
    
    for line in lines:
        # Look for part of speech pattern (noun, verb, adjective, etc.)
        if ':' in line and not definition:
            parts = line.split(':', 1)
            if len(parts) == 2:
                part_of_speech = parts[0].strip()
                definition = parts[1].strip()
        # Look for example (often in quotes or follows "Example:")
        elif '"' in line or line.lower().startswith('example'):
            example = line
    
    # If we didn't parse well, use the whole description
    if not definition:
        definition = clean_desc[:200]
    
    return {
        'word': word,
        'part_of_speech': part_of_speech,
        'definition': definition,
        'example': example
    }


def format_sms_message(word_data):
    """Format the word data into an SMS-friendly message."""
    word = word_data['word'].upper()
    pos = word_data['part_of_speech']
    definition = word_data['definition']
    example = word_data['example']
    
    # Build message with character limit in mind (~160 chars per SMS)
    message = f"Word of the Day: {word}\n\n"
    
    if pos:
        message += f"({pos}) "
    
    # Truncate definition if needed to fit in SMS
    max_def_len = 120 - len(message)
    if len(definition) > max_def_len:
        definition = definition[:max_def_len-3] + "..."
    
    message += definition
    
    # Add example if there's room
    if example and len(message) + len(example) < 300:
        message += f'\n\n{example}'
    
    return message


def send_sms(message, phone_number, gmail_address, gmail_password):
    """Send SMS via AT&T email-to-SMS gateway."""
    # AT&T SMS gateway
    sms_gateway = f"{phone_number}@txt.att.net"
    
    # Create message
    msg = MIMEText(message)
    msg['From'] = gmail_address
    msg['To'] = sms_gateway
    msg['Subject'] = ""  # SMS doesn't need subject
    
    # Send via Gmail SMTP
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_address, gmail_password)
        server.sendmail(gmail_address, sms_gateway, msg.as_string())
    
    print(f"SMS sent successfully to {phone_number}")


def main():
    # Get credentials from environment variables
    phone_number = os.environ.get('PHONE_NUMBER')
    gmail_address = os.environ.get('GMAIL_ADDRESS')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not all([phone_number, gmail_address, gmail_password]):
        raise ValueError(
            "Missing required environment variables. "
            "Please set PHONE_NUMBER, GMAIL_ADDRESS, and GMAIL_APP_PASSWORD"
        )
    
    # Remove any non-digit characters from phone number
    phone_number = re.sub(r'\D', '', phone_number)
    
    if len(phone_number) != 10:
        raise ValueError("Phone number must be 10 digits")
    
    # Fetch word of the day
    print("Fetching word of the day...")
    word_data = get_word_of_the_day()
    print(f"Today's word: {word_data['word']}")
    
    # Format and send SMS
    message = format_sms_message(word_data)
    print(f"Message:\n{message}\n")
    
    send_sms(message, phone_number, gmail_address, gmail_password)


if __name__ == "__main__":
    main()
