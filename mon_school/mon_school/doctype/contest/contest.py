# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class Contest(Document):
    def is_participant(self, email):
        return frappe.db.exists({
            'doctype': "Contest Participant",
            'contest': self.name,
            'participant': email
        })

    def add_participant(self, email):
        if self.is_participant(email):
            return
        doc = frappe.get_doc(
            doctype="Contest Participant",
            contest=self.name,
            participant=email)
        doc.insert(ignore_permissions=True)

    def remove_participant(self, email):
        filters = {
            'contest': self.name,
            'participant': email
        }
        doc = frappe.get_doc("Contest Participant", filters=filters)
        if doc:
            doc.delete()

    def get_user_submission(self, email=None):
        """Returns the submission of the current user.
        """
        email = email or frappe.session.user
        try:
            return frappe.get_doc(
                "Contest Entry",
                {"contest": self.name, "owner": email})
        except frappe.DoesNotExistError:
            return None

    def get_submission(self, name):
        """Returns the submission of the current user.
        """
        try:
            return frappe.get_doc("Contest Entry", {"contest": self.name, "name": name})
        except frappe.DoesNotExistError:
            return None

    def get_submitted_entries(self, page_size=None, start=None):
        names = frappe.db.get_all(
            "Contest Entry",
            filters={"contest": self.name, "is_submitted": True},
            pluck='name',
            start=start,
            page_length=page_size,
            order_by="modified desc")
        return [frappe.get_doc("Contest Entry", name) for name in names]

    def get_submitted_entries_count(self):
        return frappe.db.count(
            "Contest Entry",
            filters={"contest": self.name, "is_submitted": True})

    def get_participant_status(self):
        """Returns the status of the current user for this contest.
        """
        user = frappe.get_doc("User", frappe.session.user)
        submission = self.get_user_submission()
        return {
            "email": user.email,
            "user_fullname": user.full_name,
            "registered": self.is_participant(user.email),
            "submission": submission and submission.to_dict()
        }

    def get_bookmarked_entries(self, user=None):
        user = user or frappe.session.user
        filters = {"user": user, "contest": self.name}
        names = frappe.db.get_all(
            "Contest Bookmark",
            filters=filters,
            order_by="creation",
            fields=['entry'],
            pluck='entry')

        filters = {"name": ["IN", names]}
        fields = ["name", "contest", "code", "is_submitted", "owner", "image_ready"]
        rows = frappe.db.get_all(
            "Contest Entry",
            filters=filters,
            fields=fields)
        return [frappe.get_doc(dict(row, doctype="Contest Entry")) for row in rows]

@frappe.whitelist()
def join_contest(contest_name):
    if frappe.session.user == "Guest":
        return {"ok": False, "error": "Please login"}

    contest = frappe.get_doc("Contest", contest_name)
    if contest:
        contest.add_participant(frappe.session.user)
        return {"ok": True}
    else:
        return {"ok": False, "error": "Contest Not Found"}

def _update_sketch(contest, code, action):
    if frappe.session.user == "Guest":
        return _error("Please login")

    contest_doc = frappe.get_doc("Contest", contest)
    sketch = contest_doc.get_user_submission() or _new_entry(contest)

    if not contest_doc.is_active:
        return _error("Submissions are closed")

    if action == "withdraw":
        if sketch.name is None:
            return _error("No entry found to withdraw")
        if not sketch.is_submitted:
            return _error("You have not submitted an entry yet")

        sketch.is_submitted = False
        sketch.save()
    elif action == "submit":
        if sketch.is_submitted:
            return _error("Can't edit your entry after submission")
        sketch.code = code
        sketch.is_submitted = True
        if sketch.name == "new":
            sketch.insert(ignore_permissions=True)
        else:
            sketch.save(ignore_permissions=True)
    elif action == "save_draft":
        if sketch.is_submitted:
            return _error("Can't edit your entry after submission")
        sketch.code = code
        sketch.is_submitted = False
        if sketch.name == "new":
            sketch.insert(ignore_permissions=True)
        else:
            sketch.save(ignore_permissions=True)

    frappe.clear_messages()
    return _success(sketch)

def _error(message):
    return {
        "ok": False,
        "error": message
    }

def _success(sketch):
    return {
        "ok": True,
        "name": sketch.name,
        "id": sketch.sketch_id
    }

def _new_entry(contest_name):
    return frappe.get_doc({
        "doctype": "Contest Entry",
        "name": "new",
        "contest": contest_name,
        "code": "",
        "owner": frappe.session.user,
        "is_submitted": False
    })


@frappe.whitelist()
def save_entry(contest, code):
    """Save an entry to the submission as a draft.
    """
    return _update_sketch(contest, code, action="save_draft")

@frappe.whitelist()
def submit_entry(contest, code):
    """submits an entry to the submission.
    """
    return _update_sketch(contest, code, action="submit")

@frappe.whitelist()
def withdraw_entry(contest):
    """Withdraws a submitted entry from the contest.

    After this step the submitted entry will be seen as a draft.
    """
    return _update_sketch(contest, code=None, action="withdraw")

@frappe.whitelist()
def add_bookmark(entry):
    data = {
        "doctype": "Contest Bookmark",
        "entry": entry,
        "user": frappe.session.user
    }
    if not frappe.db.exists(data):
        print("exists false")
        status = "created"
        doc = frappe.get_doc(data)
        doc.insert()
    else:
        status = "aleady-present"
    return {"ok": True, "status": status}

@frappe.whitelist()
def delete_bookmark(entry):
    filters = {
        "entry": entry,
        "user": frappe.session.user
    }
    name = frappe.db.get_value("Contest Bookmark", filters=filters, fieldname='name')
    if name:
        frappe.delete_doc("Contest Bookmark", name)
        status = "deleted"
    else:
        status = "not-found"
    return {"ok": True, status: status}

@frappe.whitelist()
def update_ratings(entry, ratings):
    if isinstance(ratings, str):
        ratings = json.loads(ratings)

    try:
        entry_doc = frappe.get_doc("Contest Entry", entry)
    except frappe.DoesNotExistError:
        return {"ok": False, "error": "invalid-entry"}

    entry_doc.update_ratings(ratings)
    return {"ok": True, "status": "updated"}
