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
CSV_FILE_PATH = "../fenclaw_search/stores_with_emails.csv"
SENT_EMAILS_LOG = "sent_emails.log"
FAILED_EMAILS_LOG = "failed_emails.log"

# Email Templates by Store Type
EMAIL_TEMPLATES = {
    "tabletop game store": {
        "subject": "Wholesale Partnership for Tabletop Gaming Store",
        "template": """
Dear {store_name},

I hope this email finds you well! I'm reaching out from Fenclaw, a premium dice and gaming accessories manufacturer, to explore potential wholesale partnership opportunities with {store_name}.

We specialize in high-quality, handcrafted dice sets, gaming accessories, and unique tabletop gaming products that would be a perfect fit for your store's inventory. Our products are particularly popular among D&D players, board game enthusiasts, and collectors.

Key benefits of partnering with us:
• Premium quality, handcrafted products
• Competitive wholesale pricing
• Fast turnaround times
• Unique designs that set your store apart
• Excellent customer support

Would you be interested in receiving our wholesale catalog and pricing information? I'd love to schedule a brief call to discuss how we can help grow your gaming accessories sales.

Best regards,
[Your Name]
Fenclaw
[Your Phone Number]
[Your Website]
        """
    },
    
    "witch store": {
        "subject": "Wholesale Partnership for Spiritual & Metaphysical Store",
        "template": """
Dear {store_name},

I hope this message resonates with you! I'm reaching out from Fenclaw, a premium dice and spiritual accessories manufacturer, to explore potential wholesale partnership opportunities with {store_name}.

We create beautiful, handcrafted dice sets and spiritual tools that would complement your store's metaphysical and spiritual offerings perfectly. Our products are designed with intention and craftsmanship that your customers will appreciate.

Key benefits of partnering with us:
• Handcrafted spiritual tools and dice
• Unique designs with metaphysical significance
• Competitive wholesale pricing
• Fast production and shipping
• Products that align with spiritual practices

Would you be interested in receiving our wholesale catalog and pricing information? I'd love to discuss how our products could enhance your spiritual and metaphysical inventory.

Blessed be,
[Your Name]
Fenclaw
[Your Phone Number]
[Your Website]
        """
    },
    
    "fantasy gift shop": {
        "subject": "Wholesale Partnership for Fantasy Gift Shop",
        "template": """
Dear {store_name},

I hope this email finds you well! I'm reaching out from Fenclaw, a premium dice and fantasy accessories manufacturer, to explore potential wholesale partnership opportunities with {store_name}.

We create stunning, handcrafted dice sets and fantasy-themed accessories that would be a perfect addition to your fantasy gift shop. Our products appeal to fantasy enthusiasts, collectors, and anyone who appreciates unique, high-quality craftsmanship.

Key benefits of partnering with us:
• Unique fantasy-themed designs
• Premium handcrafted quality
• Competitive wholesale pricing
• Fast production and shipping
• Products that stand out in your store

Would you be interested in receiving our wholesale catalog and pricing information? I'd love to discuss how our fantasy accessories could enhance your product offerings.

Best regards,
[Your Name]
Fenclaw
[Your Phone Number]
[Your Website]
        """
    }
}

# Default template for unknown store types
DEFAULT_TEMPLATE = {
    "subject": "Wholesale Partnership Inquiry",
    "template": """
Dear {store_name},

I hope this email finds you well! I'm reaching out from Fenclaw, a premium dice and accessories manufacturer, to explore potential wholesale partnership opportunities with {store_name}.

We create high-quality, handcrafted products that would be a great addition to your store's inventory. Our products are popular among various customer demographics and could help diversify your offerings.

Key benefits of partnering with us:
• Premium quality, handcrafted products
• Competitive wholesale pricing
• Fast turnaround times
• Unique designs
• Excellent customer support

Would you be interested in receiving our wholesale catalog and pricing information? I'd love to schedule a brief call to discuss potential collaboration.

Best regards,
[Your Name]
Fenclaw
[Your Phone Number]
[Your Website]
    """
} 