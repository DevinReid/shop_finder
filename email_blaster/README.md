# Email Blaster - Automated Wholesale Outreach System

An automated email system that sends personalized wholesale partnership inquiries to potential clients based on store type. Built specifically for Fenclaw's wholesale outreach campaign.

## Features

- **Personalized Emails**: Different email templates for different store types (tabletop game stores, witch stores, fantasy gift shops)
- **Zoho Mail Integration**: Uses Zoho Mail API for reliable email delivery
- **Duplicate Prevention**: Automatically tracks sent emails to avoid duplicates
- **Daily Automation**: Configurable daily email limits with cron job support
- **Comprehensive Logging**: Tracks successful and failed email attempts
- **Interactive Mode**: Easy-to-use command-line interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Zoho API Credentials

```bash
python setup_env.py
```

This will create a `.env` file. You'll need to:

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new client for Zoho Mail API
3. Get your Client ID, Client Secret, and Refresh Token
4. Update the `.env` file with your actual credentials

### 3. Test the Setup

```bash
python email_blaster.py test
```

### 4. Preview Emails (Optional)

```bash
python email_blaster.py preview 3
```

### 5. Send Daily Emails

```bash
python email_blaster.py send
```

## Usage

### Interactive Mode

Run without arguments for an interactive menu:

```bash
python email_blaster.py
```

### Command Line Options

```bash
# Test the setup
python email_blaster.py test

# Preview emails without sending
python email_blaster.py preview [number]

# Send daily emails (default 5)
python email_blaster.py send [number]

# Show campaign statistics
python email_blaster.py stats
```

## Email Templates

The system includes three specialized email templates:

1. **Tabletop Game Stores**: Focuses on gaming accessories and D&D products
2. **Witch Stores**: Emphasizes spiritual and metaphysical aspects
3. **Fantasy Gift Shops**: Highlights fantasy-themed accessories

Each template is automatically selected based on the store's `query` field in the CSV.

## Automation Setup

### Windows Task Scheduler

```bash
python cron_setup.py
```

This will create a batch file and provide instructions for setting up Windows Task Scheduler.

### Linux/Mac Cron

```bash
python cron_setup.py
```

This will provide the cron command to add to your crontab.

### Manual Cron Setup

Common cron schedules:
- Daily at 9:00 AM: `0 9 * * *`
- Weekdays at 9:00 AM: `0 9 * * 1-5`
- Every 2 hours: `0 */2 * * *`

## File Structure

```
email_blaster/
├── config.py              # Configuration and email templates
├── zoho_mailer.py         # Zoho Mail API integration
├── store_processor.py     # CSV processing and email formatting
├── email_blaster.py       # Main application
├── setup_env.py           # Environment setup helper
├── cron_setup.py          # Automation setup helper
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment variables (created by setup)
├── sent_emails.log       # Log of successful emails
└── failed_emails.log     # Log of failed email attempts
```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_EMAIL=your_zoho_email@domain.com
```

### Customization

Edit `config.py` to customize:

- Daily email limit (`DAILY_EMAIL_LIMIT`)
- Email subject prefix (`EMAIL_SUBJECT_PREFIX`)
- Email templates (`EMAIL_TEMPLATES`)
- CSV file path (`CSV_FILE_PATH`)

## Data Source

The system reads from `../fenclaw_search/stores_with_emails.csv` which should contain:

- `name`: Store name
- `email`: Store email address
- `query`: Store type (used for template selection)
- `flagged`: Priority flag (optional)

## Logging

The system maintains two log files:

- `sent_emails.log`: Successfully sent emails
- `failed_emails.log`: Failed email attempts with error details

Each log entry includes timestamp, email address, store name, subject, and status.

## Troubleshooting

### Common Issues

1. **Zoho API Connection Failed**
   - Check your API credentials in `.env`
   - Verify your Zoho account has API access enabled
   - Ensure your refresh token is valid

2. **No Stores Found**
   - Check the CSV file path in `config.py`
   - Verify the CSV file exists and has the correct format
   - Check that email addresses are valid

3. **Emails Not Sending**
   - Check the failed_emails.log for specific error messages
   - Verify your Zoho account has sending permissions
   - Check for rate limiting (system includes 2-second delays)

### Testing

Always test with a small batch first:

```bash
python email_blaster.py preview 1
python email_blaster.py send 1
```

## Security Notes

- Never commit your `.env` file to version control
- Keep your Zoho API credentials secure
- The system automatically avoids sending duplicate emails
- All email attempts are logged for audit purposes

## Support

For issues or questions:
1. Check the logs in `sent_emails.log` and `failed_emails.log`
2. Test the setup with `python email_blaster.py test`
3. Verify your Zoho API credentials are correct
4. Ensure the CSV file path and format are correct 


sorted,query,city,location_id,coordinates,name,address,website,email,flagged
,tabletop game store,,,,"Test-Tabletop Game Store",123 Main St,Anytown,fenclawandfaund@gmail.com,
,witch store,,,,"Test-Witch Store",456 Main St,Anytown,fenclawandfaund@gmail.com,
,edge case games,,,,"Test-Edge Case Games",101 Main St,Anytown,fenclawandfaund@gmail.com,
,fantasy gift shop,,,,"Test-Fantasy Gift Shop",789 Main St,Anytown,fenclawandfaund@gmail.com,


1. Add video link
2. Format and Test all templates
3. Create other linesheet types
4. Edit line sheet pricing
5. add different links for each line sheet type
6. Start cleaning up email list
7. add some kind of flag to note if something has been emailed or not
8. set up cron job + jogging
9. start testing

