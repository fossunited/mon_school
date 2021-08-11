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

@frappe.whitelist()
def join_contest(contest_name):
    contest = frappe.get_doc("Contest", contest_name)
    if contest:
        contest.add_participant(frappe.session.user)
        return {"ok": True}
    else:
        return {"ok": False, "error": "Contest Not Found"}
