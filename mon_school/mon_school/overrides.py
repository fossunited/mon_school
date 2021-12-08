import frappe

from school.lms.doctype.exercise.exercise import Exercise as _Exercise
from school.lms.doctype.exercise_submission.exercise_submission import ExerciseSubmission as _ExerciseSubmission
from school.lms.doctype.lms_batch_membership.lms_batch_membership import LMSBatchMembership as _LMSBatchMembership
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

class CohortSubgroup(_CohortSubgroup):
    def get_students_with_stats(self):
        students = self.get_students()
        exercises = self.get_exercise_counts()
        runs = self.get_run_counts(students)
        sketches = self.get_sketch_counts(students)

        for s in students:
            s.num_exercises = exercises.get(s.name, 0)
            s.num_runs = runs.get(s.name, 0)
            s.num_sketches = sketches.get(s.name, 0)

        return students

    def get_exercise_counts(self):
        rows = frappe.get_all("Exercise Latest Submission",
            filters={"member_subgroup": self.name},
            fields=["member_email", "count(name) as count"],
            page_length=1000)
        return {row.member_email: row.count for row in rows}

    def get_run_counts(self, students):
        emails = [s.name for s in students]
        rows = frappe.get_all("Code Run",
            filters={"owner": ["IN", emails]},
            fields=["owner", "count(name) as count"],
            page_length=1000)
        return {row.owner: row.count for row in rows}

    def get_sketch_counts(self, students):
        emails = [s.name for s in students]
        rows = frappe.get_all("LMS Sketch",
            filters={"owner": ["IN", emails]},
            fields=["owner", "count(name) as count"],
            page_length=1000)
        return {row.owner: row.count for row in rows}
