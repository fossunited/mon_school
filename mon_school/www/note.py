import frappe

def get_context(context):
    context.no_cache = 1

    print("note get_context", frappe.form_dict)
    
    name = frappe.form_dict.get("id")
    note = get_note(name)

    if not note:
        context.template = "www/404.html"
        return

    context.note = note

def get_note(name):
    if not name:
        return

    try:
        return frappe.get_doc("Review Note", name)
    except frappe.DoesNotExistError:
        return
