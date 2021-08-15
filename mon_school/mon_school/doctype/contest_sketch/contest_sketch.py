# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ..lms_sketch.lms_sketch import LMSSketch

class ContestSketch(LMSSketch):
    def to_dict(self):
        return {
            "name": self.name,
            "code": self.code,
            "svg": self.svg,
            "image_url": self.get_image_url(mode="s"),
            "is_submitted": self.is_submitted
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
