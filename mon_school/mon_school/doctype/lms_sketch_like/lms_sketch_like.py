# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LMSSketchLike(Document):
    def after_insert(self):
        sketch = self.get_sketch()
        sketch.update_metrics()

    def after_delete(self):
        sketch = self.get_sketch()
        sketch.update_metrics()

    def get_sketch(self):
        return frappe.get_doc("LMS Sketch", self.sketch, for_update=True)


def on_doctype_update():
    # only one like for each sketch/user
    frappe.db.add_unique("LMS Sketch Like", fields=["sketch", "user"])


@frappe.whitelist()
def toggle_sketch_like(sketch_name, action):
    user = frappe.session.user

    if action == "unlike":
        frappe.get_last_doc(
            "LMS Sketch Like",
            filters={
                "user": user,
                "sketch": sketch_name,
            },
        ).delete(ignore_permissions=True)
        frappe.response["ok"] = True

    elif action == "like":
        frappe.get_doc({
            "doctype": "LMS Sketch Like",
            "user": user,
            "sketch": sketch_name,
        }).insert(ignore_permissions=True)
        frappe.response["ok"] = True

    else:
        frappe.response["ok"] = False
        frappe.response["error"] = f"Unknown action: {action}"
