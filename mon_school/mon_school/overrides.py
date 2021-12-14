import frappe
from collections import Counter
from school.lms.doctype.exercise.exercise import Exercise as _Exercise
from school.lms.doctype.exercise_submission.exercise_submission import ExerciseSubmission as _ExerciseSubmission
from school.lms.doctype.lms_batch_membership.lms_batch_membership import LMSBatchMembership as _LMSBatchMembership
from school.lms.doctype.cohort.cohort import Cohort as _Cohort
from school.lms.doctype.cohort_subgroup.cohort_subgroup import CohortSubgroup as _CohortSubgroup

from . import livecode

class Exercise(_Exercise):
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
        d = frappe.get_all("Exercise",
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
            fields=["member_email", "member_subgroup", "count(*) as count"],
            group_by="1, 2",
            page_length=10000)
        entries = [row.member_subgroup for row in rows if row.count >= num_exercises]
        num_students = self.get_students_by_subgroup()

        subgroups = {sg.name: sg for sg in self.get_subgroups()}

        result = [dict(subgroup=subgroup, count=count) for subgroup, count in Counter(entries)]
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

    def get_scores(self):
        rows = frappe.get_all("Student Score Activity",
            filters={"subgroup": self.name},
            fields=["user", "sum(score) as score"],
            group_by="user",
            page_length=1000)
        return {row.user: row.score for row in rows}
