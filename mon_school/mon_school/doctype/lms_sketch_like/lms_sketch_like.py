# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LMSSketchLike(Document):
    pass


def on_doctype_update():
    # only one like for each sketch/user
    frappe.db.add_unique("LMS Sketch Like", fields=["sketch", "user"])

    # index for faster queries
    frappe.db.add_index("LMS Sketch Like", fields=["sketch"])
    frappe.db.add_index("LMS Sketch Like", fields=["user"])
