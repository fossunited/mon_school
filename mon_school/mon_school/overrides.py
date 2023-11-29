import frappe
from collections import Counter
from lms.lms.doctype.lms_exercise.lms_exercise import LMSExercise as _Exercise
from lms.lms.doctype.exercise_submission.exercise_submission import ExerciseSubmission as _ExerciseSubmission
from lms.lms.doctype.lms_batch_membership.lms_batch_membership import LMSBatchMembership as _LMSBatchMembership
from lms.lms.doctype.cohort.cohort import Cohort as _Cohort
from lms.lms.doctype.cohort_subgroup.cohort_subgroup import CohortSubgroup as _CohortSubgroup
from frappe.website.utils import is_signup_disabled
from frappe.utils import escape_html, random_string
from frappe import _

from . import livecode

class LMSExercise(_Exercise):
    def before_save(self):
        self.image = livecode.livecode_to_svg(self.answer)

class ExerciseSubmission(_ExerciseSubmission):
    def before_save(self):
        self.image = livecode.livecode_to_svg(self.solution)

class LMSBatchMembership(_LMSBatchMembership):
    def validate_membership_in_different_batch_same_course(self):
        if self.member_type == "Mentor":
            return
        else:
            return super().validate_membership_in_different_batch_same_course()

class Cohort(_Cohort):
    def get_num_students(self, subgroup_name=None):
        filters = {"cohort": self.name}
        if subgroup_name:
            filters["subgroup"] = subgroup_name
        return frappe.db.get_value(
            "LMS Batch Membership",
            filters=filters,
            fieldname="count(*) as count")

    def get_students_by_subgroup(self):
        """Returns a dictonary mapping from subgroup to the number of students in that subgroup.
        """
        filters = {"cohort": self.name}
        rows = frappe.db.get_all(
            "LMS Batch Membership",
            filters=filters,
            fields=["subgroup", "count(*) as count"],
            group_by="subgroup")
        return {row.subgroup: row.count for row in rows}

    def get_exercises_in_course(self):
        """Returns all the exercises in the course as a dict with exercise name as the key and other details as value.
        """
        d = frappe.get_all("LMS Exercise",
                filters={"course": self.course},
                fields=["name", "title", "index_label"],
                page_length=1000)
        d = [row for row in d if row.index_label]

        def index_value(e):
            a, b = e['index_label'].split(".")
            return int(a), int(b)
        return sorted(d, key=index_value)

    def get_exercise_submission_counts(self, subgroup_name=None):
        filters = {"member_cohort": self.name}
        if subgroup_name:
            filters["member_subgroup"] = subgroup_name

        rows = frappe.get_all("Exercise Latest Submission",
            filters=filters,
            fields=["exercise", "count(*) as count"],
            group_by="1",
            order_by="2 desc",
            page_length=1000)
        return {row.exercise: row.count for row in rows}

    def get_progress_by_exercise(self, subgroup_slug=None):
        """Returns the progress by exercise in a cohort.
        """
        subgroup_name = subgroup_slug and self.get_subgroup(subgroup_slug).name

        num_students = self.get_num_students(subgroup_name)
        if num_students == 0:
            return []

        counts = self.get_exercise_submission_counts(subgroup_name)
        exercises = self.get_exercises_in_course()
        d = []
        for e in exercises:
            count = counts.get(e.name, 0)
            percent = 100*count/num_students
            entry = {
                "id": f"E{e.index_label}",
                "name": e.name,
                "title": e.title,
                "count": count,
                "num_students": num_students,
                "percent": percent
            }
            d.append(entry)
        return d

    def get_subgroup_leaderboard_by_exercises(self, num_exercises):
        """Sorts the subgroups by the percentage of students who solved more than num_exercises.
        """
        rows = frappe.get_all(
            "Exercise Latest Submission",
            filters={"member_cohort": self.name},
            fields=["member_email", "member_subgroup", "count(*) as count"],
            group_by="1, 2",
            page_length=10000)
        entries = [row.member_subgroup for row in rows if row.count >= num_exercises]
        num_students = self.get_students_by_subgroup()

        subgroups = {sg.name: sg for sg in self.get_subgroups()}

        result = [dict(subgroup=subgroup, count=count) for subgroup, count in Counter(entries).items()]
        for d in result:
            d['num_students'] = num_students[d['subgroup']]
            d['percent'] = 100*d['count']/d['num_students']
            d['title'] = subgroups[d['subgroup']].title
            d['url'] = subgroups[d['subgroup']].get_url()

        return sorted(result, key=lambda d: d['percent'], reverse=True)


class CohortSubgroup(_CohortSubgroup):
    def get_students_with_score(self):
        students = self.get_students()
        scores = self.get_scores()

        for s in students:
            s.score = scores.get(s.name, 0)
        return sorted(students, key=lambda s: s.score, reverse=True)

    def get_students_with_exercise_counts(self):
        students = self.get_students()
        counts = self.get_exercise_counts()

        for s in students:
            s.exercise_count = counts.get(s.name, 0)
        return sorted(students, key=lambda s: s.exercise_count, reverse=True)

    def get_exercise_counts(self):
        q = """
            SELECT e.member_email as email, count(*) as count
            FROM `tabExercise Latest Submission` as e
            JOIN `tabLMS Batch Membership`  as m ON m.name = e.member
            WHERE m.subgroup = %(subgroup)s
            GROUP BY 1
            ORDER BY 2 desc
        """
        rows = frappe.db.sql(q, values={"subgroup": self.name})
        return {email: count for email, count in rows}

    def get_student_progress(self, email):
        from .student_progress import StudentProgress
        p = StudentProgress(self.get_cohort().course, email)
        return p.get_progress()

    def get_scores(self):
        rows = frappe.get_all("Student Score Activity",
            filters={"subgroup": self.name},
            fields=["user", "sum(score) as score"],
            group_by="user",
            page_length=1000)
        return {row.user: row.score for row in rows}


@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name, college):
    if is_signup_disabled():
        frappe.throw(_('Sign Up is disabled'), title='Not Allowed')

    user = frappe.db.get("User", {"email": email})
    if user:
        if user.enabled:
            return 0, _("Already Registered")
        else:
            return 0, _("Registered but disabled")
    else:
        if frappe.db.get_creation_count('User', 60) > 500:
            frappe.respond_as_web_page(_('Temporarily Disabled'),
                _('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
                http_status_code=429)
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": escape_html(full_name),
        "college": college,
        "country": "",
        "enabled": 1,
        "new_password": random_string(10),
        "user_type": "Website User"
    })
    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert()

    # set default signup role as per Portal Settings
    default_role = frappe.db.get_value("Portal Settings", None, "default_role")
    if default_role:
        user.add_roles(default_role)

    if user.flags.email_sent:
        return 1, _("Please check your email for verification")
    else:
        return 2, _("Please ask your administrator to verify your sign-up")
