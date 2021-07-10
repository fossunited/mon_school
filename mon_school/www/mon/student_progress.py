from mon_school.mon_school.plugins import LiveCodeExtension
import frappe
from collections import defaultdict, Counter
from mon_school.mon_school.plugins import LiveCodeExtension

def get_context(context):
    context.no_cache = 1
    user = frappe.form_dict.get("student")
    course_name = frappe.form_dict.get("course")

    context.livecode_extension = LiveCodeExtension()

    context.user = frappe.get_doc("User", user)
    context.course = get_course(course_name)
    context.batch = get_batch(context.user)

    allowed = (
        context.batch and context.batch.is_member(frappe.session.user, member_type="Mentor")
        or "System Manager" in frappe.get_roles())

    if not allowed:
        frappe.throw('Not Permitted', frappe.PermissionError)

    if context.batch:
        course = frappe.get_doc("LMS Course", context.batch.course)
    else:
        course = get_course(course_name)
    context.report = StudentBatchReport(context.user, course, context.batch)

def get_course(course_name):
    if not course_name:
        return frappe.get_last_doc("LMS Course", filters={"is_published": 1})
    else:
        return frappe.get_doc("LMS Course", course_name)

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
        self.submissions = get_submissions(course, owner=user.name)
        self.exercises = self.get_exercises(course.name)

        self.exercises_dict = {e.name: e for e in self.get_exercises(course.name)}
        self.solutions = {s.exercise: s for s in self.submissions}
        self.lessons = self.get_lessons()
        self.exercises_by_lesson = defaultdict(list)
        for e in self.exercises:
            self.exercises_by_lesson[e.lesson].append(e)

    def get_exercises(self, course_name):
        return frappe.get_all("Exercise", {
            "course": course_name,
            "lesson": ["!=", ""]},
            ["name", "title", "description", "image", "lesson", "index_label"],
            order_by="index_")

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
        if not self.batch:
            return []
        total = len(self.exercises)
        counts = get_submission_counts(self.course, self.batch)
        students = self.course.get_students(self.batch.name)

        def progress(student):
            count = counts.get(student.email, 0)
            return {
                "student": student,
                "count": count,
                "total": total,
                "percent": self.percent(count, total)
            }

        return sorted([progress(s) for s in students], key=lambda p: p['count'], reverse=True)

def get_submissions(course, owner):
    values = {"owner": owner}

    sql = """
    select owner, exercise, lesson, batch, name, solution, creation, image
    from (
        select owner, exercise, lesson, batch, name, solution, creation, image,
            row_number() over (partition by owner, exercise order by creation desc) as ix
        from `tabExercise Submission`
        where owner=%(owner)s) as t
    where t.ix=1
    """

    return frappe.db.sql(sql, values=values, as_dict=True)

def get_submission_counts(course, batch):
    values = {"batch": batch.name}

    sql = f"""
    select owner, count(*) as count
    from (
        select owner, exercise, batch,
            row_number() over (partition by owner, exercise order by creation desc) as ix
        from `tabExercise Submission`
        where batch = %(batch)s) as t
    where t.ix=1
    group by owner
    """
    return {row.owner: row.count for row in frappe.db.sql(sql, values=values, as_dict=True)}
