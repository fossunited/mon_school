# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from school.lms.md import markdown_to_html

class ReviewNote(Document):
	def render_html(self):
		return markdown_to_html(self.note)
