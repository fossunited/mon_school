import frappe

DOCTYPE_FIELDS = {
    "Lesson": {
        "fields": ["title", "body", "chapter", "include_in_preview", "index_"],
        "fields_to_skip_on_new": ["body"]
    },
    "Chapter": {
        "fields": ["title", "description", "index_"],
    },
    "Exercise": {
        "fields": ["title", "description", "code", "answer", "course", "index_", "index_label"],
    }
}

def ensure_admin():
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Not permitted", frappe.PermissionError)

@frappe.whitelist()
def save_document(doctype, name, doc):
    ensure_admin()

    if doctype not in DOCTYPE_FIELDS:
        return {"ok": False, "error": f"Unsupport doctype: {doctype}"}

    fields = DOCTYPE_FIELDS[doctype]['fields']
    if frappe.db.exists(doctype, name):
        old_doc = frappe.get_doc(doctype, name, as_dict=True)
        old_values = [old_doc.get(k) for k in fields]
        new_values = [doc.get(k) for k in fields]
        if old_values == new_values:
            return  {"ok": True, "status": "no-change"}

        old_doc.update(doc)
        old_doc.save()
        return  {"ok": True, "status": "updated"}
    else:
        fields_to_skip_on_new = DOCTYPE_FIELDS[doctype].get("fields_to_skip_on_new")
        if fields_to_skip_on_new:
            data = dict(doc)
            data.update({k: "" for k in fields_to_skip_on_new})
            new_doc = frappe.get_doc(dict(data, doctype=doctype))
            new_doc.insert()
            frappe.rename_doc(doctype, new_doc.name, name, force=True)
            # try again now after creating a stub document
            save_document(doctype, name, doc)
        else:
            new_doc = frappe.get_doc(dict(doc, doctype=doctype))
            new_doc.insert()
            frappe.rename_doc(doctype, new_doc.name, name, force=True)
        return {"ok": True, "status": "created"}

@frappe.whitelist()
def reindex_course(course_name):
    ensure_admin()

    course = frappe.get_doc("LMS Course", course_name)
    course.reindex_lessons()
    course.reindex_exercises()
    return {"ok": True}


@frappe.whitelist(allow_guest=True)
def get_contest_entry_of_user(contest, email):
    try:
        contest_doc = frappe.get_doc("Contest", contest)
    except frappe.DoesNotExistError:
        return {"ok": False, "entry": None, "error": "contest-not-found"}

    entry = contest_doc.get_user_submission(email)
    if not entry.is_submitted:
        entry = None
    return {
        "ok": True,
        "entry": entry and entry.to_dict()
    }

@frappe.whitelist(allow_guest=True)
def get_contest_entries(contest):
    try:
        contest_doc = frappe.get_doc("Contest", contest)
    except frappe.DoesNotExistError:
        return {"ok": False, "entry": None, "error": "contest-not-found"}

    entries = contest_doc.get_submitted_entries()
    return {
        "ok": True,
        "entries": [entry.to_dict() for entry in entries]
    }