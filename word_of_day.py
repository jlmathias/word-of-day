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
    
    # Parse the description HTML
    description = entry.description
    
    # Extract part of speech - appears after bullet as <em>adjective</em>
    # Pattern: • \pronunciation\ • <em>part_of_speech</em>
    pos_match = re.search(r'\\[^\\]+\\[^<]*<em>(\w+)</em>', description)
    part_of_speech = pos_match.group(1).strip() if pos_match else ""
    
    # Extract definition - the paragraph that explains what the word means
    # It typically contains the word in <em> tags and describes it
    # Look for <p><em>Word</em> describes/means/is...
    def_match = re.search(
        rf'<p>\s*<em>{re.escape(word)}</em>\s+([^<]+(?:<[^>]+>[^<]*)*?)</p>',
        description,
        re.IGNORECASE
    )
    if def_match:
        definition = def_match.group(1)
        definition = re.sub(r'<[^>]+>', '', definition)
        definition = unescape(definition).strip()
        # Capitalize first letter
        if definition:
            definition = definition[0].upper() + definition[1:]
    else:
        # Fallback: find paragraphs and pick the definition-like one
        definition = ""
        paragraphs = re.findall(r'<p>(.*?)</p>', description, re.DOTALL)
        for p in paragraphs:
            clean_p = re.sub(r'<[^>]+>', '', p)
            clean_p = unescape(clean_p).strip()
            # Look for descriptive text (not examples, not links)
            if (clean_p and 
                not clean_p.startswith('//') and 
                'See the entry' not in clean_p and
                'Examples:' not in clean_p and
                word.lower() in clean_p.lower() and
                len(clean_p) > 30):
                definition = clean_p
                break
    
    # Extract example sentence (starts with //)
    example_match = re.search(r'//\s*([^<]+)', description)
    if example_match:
        example = example_match.group(1)
        example = re.sub(r'<[^>]+>', '', example)
        example = unescape(example).strip()
        # Remove trailing period if present, then wrap in quotes
        example = example.rstrip('.')
        example = f'"{example}."'
    else:
        example = ""
    
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
