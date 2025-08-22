__version__ = "0.0.1"




import erpnext.crm.doctype.email_campaign.email_campaign as email_campaign_module
from v3bid.v3bid.custom_email_send import (
    custom_send_email_to_leads_or_contacts,
    custom_send_mail,
)


def patch_email_campaign():
    print(" Patching Email Campaign Module with Custom Methods...----------------------------------------------------------")
    email_campaign_module.send_email_to_leads_or_contacts = custom_send_email_to_leads_or_contacts
    email_campaign_module.send_mail = custom_send_mail


# Call patch function when app loads
patch_email_campaign()


