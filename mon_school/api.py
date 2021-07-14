import frappe

DOCTYPE_FIELDS = {
    "Lesson": {
        "fields": ["title", "body", "chapter", "include_in_preview"],
        "fields_to_skip_on_new": ["body"]
    },
    "Chapter": {
        "fields": ["title", "description"],
    },
    "Exercise": {
        "fields": ["title", "description", "code", "answer", "course"],
    }
}

@frappe.whitelist()
def save_document(doctype, name, doc):
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
            frappe.rename_doc(doctype, new_doc.name, name)
        return {"ok": True, "status": "created"}

@frappe.whitelist()
def reindex_course(course_name):
    course = frappe.get_doc("LMS Course", course_name)
    course.reindex_lessons()
    course.reindex_exercises()
    return {"ok": True}