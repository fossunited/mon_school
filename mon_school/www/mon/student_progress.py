from mon_school.mon_school.plugins import LiveCodeExtension
import frappe
from collections import defaultdict, Counter
from mon_school.mon_school.plugins import LiveCodeExtension

def get_context(context):
    context.no_cache = 1
    user = frappe.form_dict.get("student")

    context.livecode_extension = LiveCodeExtension()

    context.user = frappe.get_doc("User", user)
    context.batch = get_batch(context.user)

    if context.batch:
        course = frappe.get_doc("LMS Course", context.batch.course)
        context.report = StudentBatchReport(context.user, course, context.batch)

def get_batch(user):
    batch_name = frappe.db.get_value(
        "LMS Batch Membership",
        filters={"member": user.name, "member_type": "Student"},
        fieldname="batch")
    return batch_name and frappe.get_doc("LMS Batch", batch_name)

class StudentBatchReport:
    def __init__(self, user, course, batch):
        self.user = user
        self.course = course
        self.batch = batch
        self.students = course.get_students(batch.name)
        self.submissions = get_submissions(user.name, course, batch)
        self.exercises = self.get_exercises(course.name)

        self.exercises_dict = {e.name: e for e in self.get_exercises(course.name)}
        self.solutions = {s.exercise: s for s in self.submissions}
        self.lessons = self.get_lessons()
        self.exercises_by_lesson = defaultdict(list)
        for e in self.exercises:
            self.exercises_by_lesson[e.lesson].append(e)

    def get_exercises(self, course_name):
        return frappe.get_all("Exercise", {"course": course_name, "lesson": ["!=", ""]}, ["name", "title", "description", "image", "lesson", "index_label"], order_by="index_label")

    def get_status_of_exercises(self, lesson_name):
        d = []
        for e in self.exercises_by_lesson[lesson_name]:
            d.append({"exercise": self.exercises_dict[e.name], "submission": self.solutions.get(e.name)})
        return d

    def get_submissions_of_exercise(self, exercise_name):
        return self.submissions_by_exercise[exercise_name]

    def get_lessons(self):
        return [lesson
                for c in self.course.get_chapters()
                for lesson in c.get_lessons()]

    def get_progress_by_lesson(self, lesson_name):
        count = sum(1 for e in self.exercises if e.lesson == lesson_name)
        value = sum(1 for s in self.submissions if s.lesson == lesson_name)

        print("progress", lesson_name, count, value)

        return {
            "value": value,
            "count": count,
            "percent": self.percent(value, count)
        }
    def percent(self, value, count):
        if not count:
            return 0
        else:
            return value/count*100

    def get_progress_by_student(self):
        total = len(self.exercises)
        counts = Counter(s.owner.email for s in self.submissions)

        print("counts", counts)

        def progress(student):
            count = counts.get(student.email, 0)
            return {
                "student": student,
                "count": count,
                "total": total,
                "percent": self.percent(count, total)
            }

        return sorted([progress(s) for s in self.students], key=lambda p: p['count'], reverse=True)

def get_submissions(user, course, batch):
    values = {"batch": batch.name, "owner": user}
    sql = """
    select owner, exercise, lesson, batch, name, solution, creation, image
    from (
        select owner, exercise, lesson, batch, name, solution, creation, image,
            row_number() over (partition by owner, exercise order by creation desc) as ix
        from `tabExercise Submission`
        where owner=%(owner)s) as t
    where t.ix=1 and t.batch = %(batch)s
    """

    return frappe.db.sql(sql, values=values, as_dict=True)
