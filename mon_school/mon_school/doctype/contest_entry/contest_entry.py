# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
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

    def get_ratings(self, user=None):
        """Returns the ratings for this entry from the specified user as a dict.

        The `user` defaults to the current user is not specified.

        The output would be in the following format:

            {
                "Novelty": 5,
                "Color Composition": 4,
                "Complexity": 3
            }

        The keys would be the categories under which the entry is rated on
        and the value is the rating given by the user in the scale of 0 to 5.

        Returns None if no rating is providied by the user for this entry.
        """
        filters = {
            "user": user or frappe.session.user,
            "entry": self.name
        }
        name = frappe.db.get_value(
            "Contest Entry Review",
            filters=filters,
            fieldname="name")
        if not name:
            return

        review = frappe.get_doc("Contest Entry Review", name)
        return {rating.category: rating.rating for rating in review.ratings}

    def update_ratings(self, ratings, user=None):
        """Updates the ratings for this entry by a user.
        """
        user = user or frappe.session.user
        ratings_list = [{"category": k, "rating": v} for k, v in ratings.items()]

        filters = {
            "user": user,
            "entry": self.name
        }
        name = frappe.db.get_value(
            "Contest Entry Review",
            filters=filters,
            fieldname="name")
        if name is None:
            doc = frappe.get_doc({
                "doctype": "Contest Entry Review",
                "entry": self.name,
                "user" : user,
            })
            doc.update({"ratings": ratings_list})
            doc.insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Contest Entry Review", name)
            doc.update({"ratings": ratings_list})
            doc.save(ignore_permissions=True)
