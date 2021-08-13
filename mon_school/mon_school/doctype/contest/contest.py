# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

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

    def get_user_submission(self):
        """Returns the submission of the current user.
        """
        try:
            return frappe.get_doc("Contest Sketch", {"contest": self.name, "owner": frappe.session.user})
        except frappe.DoesNotExistError:
            return None

    def get_submission(self, name):
        """Returns the submission of the current user.
        """
        try:
            return frappe.get_doc("Contest Sketch", {"contest": self.name, "name": name})
        except frappe.DoesNotExistError:
            return None

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

@frappe.whitelist()
def save_submission(contest, code):
    if frappe.session.user == "Guest":
        return {"ok": False, "error": "Please login"}

    contest_doc = frappe.get_doc("Contest", contest)
    sketch = contest_doc.get_user_submission()

    if not sketch:
        sketch = frappe.new_doc("Contest Sketch")
        sketch.contest = contest
        sketch.code = code
        sketch.insert(ignore_permissions=True)
        print("created new submission for ", frappe.session.user, sketch.name)
    else:
        print("updating existing submission for ", frappe.session.user, sketch.name)
        sketch.code = code
        sketch.svg = ''
        sketch.save()
    return {
        "ok": True,
        "name": sketch.name,
        "id": sketch.sketch_id
    }
