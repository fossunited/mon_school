# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ..lms_sketch.lms_sketch import LMSSketch

class ContestEntry(LMSSketch):
    def to_dict(self, include_author=False):
        owner = self.get_owner()
        return {
            "name": self.name,
            "image_url": self.get_image_url(mode="s"),
            "s_image_url": self.get_image_url(mode="s"),
            "m_image_url": self.get_image_url(mode="m"),
            "is_submitted": self.is_submitted,
            "author": {
                "full_name": owner.full_name,
                "username": owner.username
            }
        }

    @property
    def title(self):
        # XXX-Anand: fix this
        return "Pookkalam"

    @property
    def sketch_id(self):
        """Returns the unique id to reference the contest sketch.

        This will be x-{name}
        """
        return 'x-' + self.name

    @property
    def runtime(self):
        return "joy"
