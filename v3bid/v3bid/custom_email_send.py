
import frappe
from frappe.core.doctype.communication.email import make
import erpnext.crm.doctype.email_campaign.email_campaign as email_campaign_module



from datetime import datetime, timedelta
from frappe.utils import getdate, today, add_days

def custom_send_email_to_leads_or_contacts_mail():
    now = datetime.now()
    print(f"Custom send_email_to_leads_or_contacts running at {now} --------------------")

    email_campaigns = frappe.get_all(
        "Email Campaign",
        filters={"status": ("not in", ["Unsubscribed", "Completed", "Scheduled"])}
    )

    for camp in email_campaigns:
        email_campaign = frappe.get_doc("Email Campaign", camp.name)

        # Check if today is within start_date and end_date
        if email_campaign.start_date <= getdate(today()) <= email_campaign.end_date:

            # Ensure custom_time exists
            if hasattr(email_campaign, "custom_time") and email_campaign.custom_time:
                campaign_time = email_campaign.custom_time

                # Convert timedelta or string to datetime
                if isinstance(campaign_time, timedelta):
                    campaign_datetime = datetime.combine(datetime.today(), datetime.min.time()) + campaign_time
                elif isinstance(campaign_time, str):
                    h, m, s = map(int, campaign_time.split(":"))
                    campaign_datetime = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=h, minutes=m, seconds=s)
                else:
                    print(f"Unknown type for custom_time in {email_campaign.name}")
                    continue

                # Execute campaign if current time is ±1 minute of custom_time
                if abs((now - campaign_datetime).total_seconds()) < 60:
                    print(f"Executing campaign: {email_campaign.name} at {now}")

                    # Call custom_send_mail for each schedule
                    campaign = frappe.get_cached_doc("Campaign", email_campaign.campaign_name)
                    for entry in campaign.get("campaign_schedules"):
                        scheduled_date = add_days(email_campaign.get("start_date"), entry.get("send_after_days"))
                        if scheduled_date == getdate(today()):
                            custom_send_mail(entry, email_campaign)

                else:
                    print(f"Skipped campaign {email_campaign.name} (Scheduled at {campaign_datetime.time()})")
            else:
                print(f"Campaign {email_campaign.name} has no custom_time set.")
        else:
            print(f"Campaign {email_campaign.name} skipped (Out of Date Range)")



def custom_send_mail(entry, email_campaign):
    
    print("custom_this is send mail methods------------------------------------------------------")
     

    recipient_list = []
    if email_campaign.email_campaign_for == "Email Group":
        for member in frappe.db.get_list(
            "Email Group Member",
            filters={"email_group": email_campaign.get("recipient")},
            fields=["email"]
        ):
            recipient_list.append(member["email"])
    else:
        recipient = frappe.db.get_value(
            email_campaign.email_campaign_for,
            email_campaign.get("recipient"),
            "email_id"
        )
        if recipient:
            recipient_list.append(recipient)

    email_template = frappe.get_doc("Email Template", entry.get("email_template"))
    sender = frappe.db.get_value("User", email_campaign.get("sender"), "email")

    # Loop through each recipient and send mail individually
    for recipient in recipient_list:
        context = {
            "doc": frappe.get_doc(email_campaign.email_campaign_for, email_campaign.recipient)
        }
        comm = make(
            doctype="Email Campaign",
            name=email_campaign.name,
            subject=frappe.render_template(email_template.get("subject"), context),
            content=frappe.render_template(email_template.response_, context),
            sender=sender,
            recipients=recipient,
            communication_medium="Email",
            sent_or_received="Sent",
            send_email=True,
            email_template=email_template.name,
        )
        print(f"Mail sent to {recipient}")

    return "All mails sent successfully"




def custom_send_email_to_leads_or_contacts():
    # frappe.log_error("this is custom mehtods email ------------------------------------------------------------")
    print("this custom method running ----------------------------------------------------------------------")
    
    return

setattr(email_campaign_module, "send_email_to_leads_or_contacts", custom_send_email_to_leads_or_contacts)

setattr(email_campaign_module, "send_mail", custom_send_mail)


