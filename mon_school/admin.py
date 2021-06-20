"""Admin APIs to setup batches in mon_school.
"""
import frappe
from frappe import _
from frappe.utils import escape_html, random_string
from community.lms.doctype.lms_batch_membership.lms_batch_membership import create_membership
import json

def sign_up(email, full_name):
    user = frappe.db.get("User", {"email": email})
    if user:
        if user.disabled:
            return 0, _("Registered but disabled")
        else:
            return 0, _("Already Registered")
    else:
        if frappe.db.sql("""select count(*) from tabUser where
            HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 300:

            frappe.respond_as_web_page(_('Temporarily Disabled'),
                _('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
                http_status_code=429)

        from frappe.utils import random_string
        user = frappe.get_doc({
            "doctype":"User",
            "email": email,
            "first_name": escape_html(full_name),
            "enabled": 1,
            "new_password": random_string(10),
            "user_type": "Website User"
        })
        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.insert()

        # set default signup role as per Portal Settings
        default_role = frappe.db.get_value("Portal Settings", None, "default_role")
        if default_role:
            user.add_roles(default_role)

    return "done"

@frappe.whitelist()
def setup_batch(batch_name, users):
    current_user = frappe.get_doc("User", frappe.session.user)
    if 'System Manager' not in [role.role for role in current_user.roles]:
        raise Exception("permission Denied")

    batch = frappe.get_doc("LMS Batch", batch_name)

    result = {}
    users = json.loads(users)
    for user in users:
        email = user['email']
        full_name = user['full_name']
        r = result.setdefault(email, {})

        if frappe.db.exists("User", email):
            r['signup'] = 'already signed up'
        else:
            r['signup'] = sign_up(email, full_name)

        if batch.is_member(email):
            r['batch'] = 'already member'
        else:
            create_membership(batch_name, email)
            r['batch'] = 'added'

    return result
