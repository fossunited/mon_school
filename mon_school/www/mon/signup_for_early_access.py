import frappe
from frappe import request
from urllib.parse import urlencode

def get_context(context):
    course_name = frappe.form_dict.get("course")
    course = course_name and get_course(course_name)
    if not course:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?" + urlencode({"redirect-to": request.full_path})
        raise frappe.Redirect

    data = {
        "doctype": "LMS Course Interest",
        "user": frappe.session.user,
        "course": course.name
    }

    if course.upcoming and not frappe.db.exists(data):
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

    frappe.local.flags.redirect_location = f"/courses/{course_name}"
    raise frappe.Redirect
    print("Redirected!")

def get_course(course_name):
    return frappe.get_doc("LMS Course", course_name)

def already_signed_up(course):
    filters = {"course": course.name, "user": frappe.session.user}
    return frappe.db.exists("LMS Course Interest", filters=filters)
