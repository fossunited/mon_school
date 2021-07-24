"""API methods for creating new batches.
"""
import frappe
import re

def ensure_admin():
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Not permitted", frappe.PermissionError)

class BatchRequest:
    def __init__(self, name, students, mentors):
        self.name = name
        self.students = students
        self.mentors = mentors
        self.batch = None

    def process(self):
        response = {}
        response['batch'] = self.process_batch()
        response['students'] = self.process_students()
        response['mentors'] = self.process_mentors()
        return response

    def process_batch(self):
        try:
            self.batch = frappe.get_last_doc("LMS Batch", filters={"title": self.name})
            return "present"
        except frappe.exceptions.DoesNotExistError as e:
            self.batch = frappe.get_doc({
                "doctype": "LMS Batch",
                "title": self.name,
                "description": "",
                "course": "the-joy-of-programming",
                "visibility": "Unlisted",
                "membership": "Invite Only",

                # unused fields
                "start_date": "2021-07-01",
                "sessions_on": "anytime",
                "start_time": "16:00",
                "end_time": "17:00",
            })
            self.batch.insert()
            return "created"

    def process_students(self):
        result = []

        for s in self.students:
            status = dict(s)
            status['user'] = self.ensure_user(s['name'], s['email'])
            status['membership'] = self.add_member(self.batch.name, s['email'], member_type="Student")
            result.append(status)

        return result

    def process_mentors(self):
        result = []

        for mentor in self.mentors:
            status = dict(mentor)
            status['user'] = self.ensure_user(mentor['name'], mentor['email'])
            status['membership'] = self.add_member(self.batch.name, mentor['email'], member_type="Mentor")
            result.append(status)
        return result

    def ensure_user(self, name, email):
        try:
            user = frappe.get_doc("User", email)
            return "present"
        except frappe.DoesNotExistError:
            user = frappe.get_doc({
                "doctype": "User",
                "first_name": name,
                "email": email,
                "username": self.suggest_username(name)
            })
            user.insert()
            return "created"

    def add_member(self, batch_name, email, member_type):
        result = frappe.get_all("LMS Batch Membership", filters={"batch": batch_name, "member": email})
        if result:
            return "present"

        doc = frappe.get_doc({
            "doctype": "LMS Batch Membership",
            "batch": batch_name,
            "member": email,
            "member_type": member_type})
        doc.insert()
        return "added"

    def sanitize_name(self, name):
        return re.sub("\s+", " ", name).strip()

    def has_username(self, username):
        if len(username) < 5:
            return True

        result = frappe.db.get_all("User", filters={"username": username})
        return len(result) > 0

    def suggest_username(self, name):
        username = name.strip().split()[0].lower()
        if len(username) < 4 or self.has_username(username):
            username = name.replace(" ", "").lower()

        if not self.has_username(username):
            return username

        for i in range(2, 100):
            new_usename = f"{username}{i}"
            if not self.has_username(new_usename):
                return new_usename

        raise Exception("Failed to suggest username for " + name)

@frappe.whitelist()
def create_batch(data):
    ensure_admin()
    request = BatchRequest(
        name=data['name'],
        students=data['students'],
        mentors=data['mentors'])
    return request.process()
