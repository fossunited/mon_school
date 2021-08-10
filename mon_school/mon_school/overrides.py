import frappe

from community.lms.doctype.exercise.exercise import Exercise as _Exercise
from community.lms.doctype.exercise_submission.exercise_submission import ExerciseSubmission as _ExerciseSubmission
from community.lms.doctype.lms_batch_membership.lms_batch_membership import LMSBatchMembership as _LMSBatchMembership

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

