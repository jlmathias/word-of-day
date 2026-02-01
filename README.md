# Word of the Day SMS Service

A simple service that texts you Merriam-Webster's word of the day every morning.

## How It Works

1. GitHub Actions runs daily at 8:00 AM Pacific Time
2. A Python script fetches the word of the day from Merriam-Webster's RSS feed
3. The word, definition, and example are sent to your phone via AT&T's email-to-SMS gateway

## Setup Instructions

### Step 1: Create a Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if you haven't already
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and "Other (Custom name)"
5. Name it "Word of the Day SMS"
6. Copy the 16-character password that's generated

### Step 2: Create a GitHub Repository

1. Create a new repository on GitHub
2. Push this code to your repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 3: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** and add these three secrets:

| Secret Name | Value |
|-------------|-------|
| `PHONE_NUMBER` | Your 10-digit phone number (e.g., `5551234567`) |
| `GMAIL_ADDRESS` | Your Gmail address (e.g., `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character app password from Step 1 |

### Step 4: Test It

1. Go to the **Actions** tab in your repository
2. Click on "Daily Word of the Day SMS"
3. Click **Run workflow** > **Run workflow**
4. You should receive an SMS within a minute!

## Customization

### Change the Time

Edit `.github/workflows/daily-word.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '0 16 * * *'  # 8 AM Pacific (UTC-8)
```

Cron format: `minute hour day month weekday` (in UTC)

Common times:
- `0 14 * * *` = 6 AM Pacific
- `0 16 * * *` = 8 AM Pacific
- `0 18 * * *` = 10 AM Pacific

### Different Phone Carrier

If you're not on AT&T, edit `word_of_day.py` and change the SMS gateway in the `send_sms` function:

| Carrier | Gateway |
|---------|---------|
| AT&T | `@txt.att.net` |
| Verizon | `@vtext.com` |
| T-Mobile | `@tmomail.net` |
| Sprint | `@messaging.sprintpcs.com` |

## Local Testing

You can test locally by setting environment variables:

```bash
export PHONE_NUMBER="5551234567"
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"

pip install -r requirements.txt
python word_of_day.py
```

## Cost

**Completely free!**
- GitHub Actions: 2,000 minutes/month free (this uses ~30 seconds/day)
- Email-to-SMS: Free through your carrier's gateway
- No API keys or paid services required

## Troubleshooting

**Not receiving texts?**
- Check that your phone number is exactly 10 digits
- Verify the Gmail App Password is correct (not your regular password)
- Make sure your carrier's SMS gateway is correct
- Check the Actions tab for error logs

**Texts arriving late?**
- GitHub Actions cron jobs can be delayed by up to 15 minutes during high load
- Consider adjusting the schedule time to account for this
