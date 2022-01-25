from re import L
from shutil import ignore_patterns
import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/account/subdomain"
        raise frappe.Redirect

    context.subdomain = get_subdomain()

def get_subdomain():
    doctype = "Mon School User Subdomain"
    name = frappe.db.exists(doctype, {"user": frappe.session.user})
    if name:
        return frappe.get_doc(doctype, name)
    else:
        user = frappe.get_doc("User", frappe.session.user)
        return frappe.get_doc({
            "doctype": doctype,
            "user": user.name,
            "subdomain": user.username,
            "ip": ""
        })

@frappe.whitelist()
def save_subdomain(ip):
    doctype = "Mon School User Subdomain"
    name = frappe.db.exists(doctype, {"user": frappe.session.user})
    user = frappe.get_doc("User", frappe.session.user)
    if name:
        doc = frappe.get_doc(doctype, name)
        doc.ip = ip
        doc.subdomain = user.username
        doc.save("ignore_permissions", True)
    else:
        doc = frappe.get_doc({
            "doctype": doctype,
            "user": user.name,
            "subdomain": user.username,
            "ip": ip
        })
        doc.insert(ignore_permissions=True)
    frappe.msgprint("Successfully updated the IP address of your subdomain.")
    return {"ok": True}
