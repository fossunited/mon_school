# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LMSSketchLike(Document):
    def after_insert(self):
        sketch = self.get_sketch()
        sketch.update_metrics()

    def get_sketch(self):
        return frappe.get_doc("LMS Sketch", self.sketch)


def on_doctype_update():
    # only one like for each sketch/user
    frappe.db.add_unique("LMS Sketch Like", fields=["sketch", "user"])

    # index for faster queries
    frappe.db.add_index("LMS Sketch Like", fields=["sketch"])
    frappe.db.add_index("LMS Sketch Like", fields=["user"])


@frappe.whitelist()
def toggle_like_sketch(sketch_name):
    user = frappe.session.user
    sketch = frappe.get_doc("LMS Sketch", sketch_name)

    if sketch.is_liked_by(user):
        frappe.db.delete("LMS Sketch Like", {"user": user, "sketch": sketch_name})
        # TODO (nikochiko): after_delete is not working, so we need
        # this update_metrics here, fix after_delete and move it there
        sketch.update_metrics()
    else:
        frappe.get_doc({
            "doctype": "LMS Sketch Like",
            "user": user,
            "sketch": sketch_name,
        }).insert(ignore_permissions=True)

    frappe.response["ok"] = True
