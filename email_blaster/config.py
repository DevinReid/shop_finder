import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Zoho Mail API Configuration
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID', '')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET', '')
ZOHO_REFRESH_TOKEN = os.getenv('ZOHO_REFRESH_TOKEN', '')
ZOHO_EMAIL = os.getenv('ZOHO_EMAIL', '')

# Email Settings
DAILY_EMAIL_LIMIT = 5
EMAIL_SUBJECT_PREFIX = "Wholesale Partnership Inquiry - "

# File Paths
TEST_CSV_FILE_PATH = "../fenclaw_search/Test_email_blaster.csv"
CSV_FILE_PATH = "C:/Users/Dreid/Desktop/Brain/Projects/shop_finder/email_blaster/cleaned_stores_with_emails.csv"

SENT_EMAILS_LOG = "sent_emails.log"
FAILED_EMAILS_LOG = "failed_emails.log"

# Email Templates by Store Type
EMAIL_TEMPLATES = {
    "tabletop game store": {
        "subject": "Do you dare join the Cult of Mathilda?🕷️",
        "template": """
<p><strong>Magical items from an indie brand you haven't met yet</strong></p>
<p>Greetings from New Orleans ⚜️</p>
<p>My husband and I run a small fantasy brand called <a href='https://www.fenclawandfaund.com' target='_blank'>Fenclaw & Faund</a>, where we create magical items and share the lore behind them. We discovered your gaming shop, {store_name}, and think our <strong>Cult of Mathilda Spell Book and Runic Die Set</strong> would be a great fit for your players who enjoy TTRPGs 🧙‍♂️</p>
<p>I have included our <strong>linesheet</strong> plus a video explaining how to use the runic dice and spell book as a tool for gaming.</p>
<p>Let us know your thoughts ~ we're happy to <strong>answer any questions you have</strong> and we can work with you on pricing depending on what you'd like to order ✨</p>
<p>Cheers,<br>Tessla<br>Portal Keeper, Fenclaw & Faund</p>
<p><strong>Linesheet:</strong> <a href="https://docs.google.com/presentation/d/1m9QdJ4AJPLAt5E1L1dPNr9R8q4ZYM2k0N54EVqZr0rE/edit?usp=sharing" target="_blank">View & Download Here</a></p>
<p><strong>Spell Book Video Demo:</strong> <a href="https://youtube.com/shorts/zdgHhfXKCWI" target="_blank">Learn How to Use the Spell Book</a></p>
"""
    },
    
    "witch store": {
        "subject": "Could Fenclaw & Faund enchant your shelves?🔮",
        "template": """
<p><strong>Created by a tiny team with big magic energy, discover our wares</strong></p>
<p>Greetings from New Orleans ⚜️</p>
<p>My husband and I run a small fantasy brand called <a href='https://www.fenclawandfaund.com' target='_blank'>Fenclaw & Faund</a>, where we create magical items and share the lore behind them. We discovered your fantastic shop, {store_name}, and think some of our items - particularly our <strong>Cult of Mathilda Spell Book</strong> or <strong>Runic Beanie</strong> would be a perfect addition to your store.</p>
<p>I have included our <strong>linesheet</strong> plus a video explaining how to use the spell book as it comes with a pair of runic dice for randomized spell casting.</p>
<p>Let us know your thoughts ~ we're happy to <strong>answer any questions you have</strong> and we can work with you on pricing depending on what you'd like to order ✨</p>
<p>Cheers,<br>Tessla<br>Portal Keeper, Fenclaw & Faund</p>
<p><strong>Linesheet:</strong> <a href="https://docs.google.com/presentation/d/1m9QdJ4AJPLAt5E1L1dPNr9R8q4ZYM2k0N54EVqZr0rE/edit?usp=sharing" target="_blank">View & Download Here</a></p>
<p><strong>Spell Book Video Demo:</strong> <a href="https://youtube.com/shorts/zdgHhfXKCWI" target="_blank">Learn How to Use the Spell Book</a></p>
"""
    },
    
    "fantasy gift shop": {
        "subject": "Could Fenclaw & Faund enchant your shelves?🔮",
        "template": """
<p><strong>Created by a tiny team with big magic energy, discover our wares</strong></p>
<p>Greetings from New Orleans ⚜️</p>
<p>My husband and I run a small fantasy brand called <a href='https://www.fenclawandfaund.com' target='_blank'>Fenclaw & Faund</a>, where we create magical items and share the lore behind them. We discovered your fantasy gift shop, {store_name}, and think items such as our Cult of Mathilda <strong>Spell Book and Runic Die Set</strong>, <strong>Perfume Oil of the Urchin's Kiss</strong>, or <strong>Brocade Pirate Pants</strong> would delight your customers looking for a truly unique item.</p>
<p>I have included our <strong>linesheet</strong> plus a video explaining how to use the spell book as it comes with a pair of runic dice for randomized spell casting.</p>
<p>Let us know your thoughts ~ we're happy to <strong>answer any questions you have</strong> and we can work with you on pricing depending on what you'd like to order ✨</p>
<p>Cheers,<br>Tessla<br>Portal Keeper, Fenclaw & Faund</p>
<p><strong>Linesheet:</strong> <a href="https://docs.google.com/presentation/d/1m9QdJ4AJPLAt5E1L1dPNr9R8q4ZYM2k0N54EVqZr0rE/edit?usp=sharing" target="_blank">View & Download Here</a></p>
<p><strong>Spell Book Video Demo:</strong> <a href="https://youtube.com/shorts/zdgHhfXKCWI" target="_blank">Learn How to Use the Spell Book</a></p>
"""
    }
}

# Default template for unknown store types
DEFAULT_TEMPLATE = {
    "subject": "Wholesale Partnership Inquiry",
    "template": """
<p>Dear {store_name},</p>

<p>I hope this email finds you well! I'm reaching out from Fenclaw, a premium dice and accessories manufacturer, to explore potential wholesale partnership opportunities with {store_name}.</p>

<p>We create high-quality, handcrafted products that would be a great addition to your store's inventory. Our products are popular among various customer demographics and could help diversify your offerings.</p>

<p>Key benefits of partnering with us:</p>
<ul>
<li>Premium quality, handcrafted products</li>
<li>Competitive wholesale pricing</li>
<li>Fast turnaround times</li>
<li>Unique designs</li>
<li>Excellent customer support</li>
</ul>

<p>Would you be interested in receiving our wholesale catalog and pricing information? I'd love to schedule a brief call to discuss potential collaboration.</p>

<p>Best regards,</p>
<p>- Tessla and Devin</p>
<p>Fenclaw & Faund</p>
<p>714-350-8349</p>
<p>Fenclawandfaund.com</p>
    """
}

LINESHEET_PATH = "line_sheet.pdf" 