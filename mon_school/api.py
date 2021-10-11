import frappe

DOCTYPES = [
    "LMS Course",
    "Course Chapter",
    "Course Lesson",
    "Exercise"
]

def ensure_admin():
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Not permitted", frappe.PermissionError)

def get_course(doc):
    """Returns the course name for given document of type Course, Chapter, Lesson or Exercise.
    """
    if doc.doctype == "LMS Course":
        return doc.name
    elif doc.doctype == "Course Chapter":
        return doc.course
    elif doc.doctype == "Exercise":
        return doc.course
    elif doc.doctype == "Course Lesson":
        chapter = frappe.get_doc(doc.chapter)
        return chapter.course
    else:
        return

def can_edit(doctype, name, doc_data):
    if "System Manager" in frappe.get_roles():
        return True

    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
        course_name = get_course(doc)
    else:
        new_doc = frappe.get_doc(dict(doc_data, doctype=doctype))
        course_name = get_course(new_doc)

    if not course_name or not frappe.db.exists("LMS Course", course_name):
        return False

    course = frappe.get_doc("LMS Course", course_name)
    return course.author == frappe.session.user

@frappe.whitelist()
def save_document(doctype, name, doc):
    if not can_edit(doctype, name, doc):
        frappe.throw("Not permitted", frappe.PermissionError)

    if doctype not in DOCTYPES:
        return {"ok": False, "error": f"Unsupport doctype: {doctype}"}

    if frappe.db.exists(doctype, name):
        old_doc = frappe.get_doc(doctype, name, as_dict=True)
        old_doc.update(doc)
        old_doc.save()
        return  {"ok": True, "status": "updated"}
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
        _clear_messages()
        return {"ok": False, "entry": None, "error": "contest-not-found"}

    entry = contest_doc.get_user_submission(email)
    if entry and not entry.is_submitted:
        entry = None
    if entry is None:
        _clear_messages()

    return {
        "ok": True,
        "entry": entry and entry.to_dict()
    }

def _clear_messages():
    frappe.clear_messages()
    frappe.local.response.pop('exc_type', None)

@frappe.whitelist(allow_guest=True)
def get_contest_entries(contest):
    try:
        contest_doc = frappe.get_doc("Contest", contest)
    except frappe.DoesNotExistError:
        _clear_messages()
        return {"ok": False, "entry": None, "error": "contest-not-found"}

    entries = contest_doc.get_submitted_entries()
    return {
        "ok": True,
        "entries": [entry.to_dict() for entry in entries]
    }
