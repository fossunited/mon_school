import frappe
from collections import defaultdict, Counter

def get_context(context):
    context.no_cache = 1
    context.user = get_user()

    batch_name = frappe.form_dict.get("batch")

    context.batches = get_batches(context.user)
    context.batch = select_batch(context.batches, batch_name)
    context.mentors = get_mentors(context.batch.course, context.batch.name)

    if context.batch:
        course = frappe.get_doc("LMS Course", context.batch.course)
        context.report = BatchReport(course, context.batch)

def get_user():
    if frappe.session.user != "Guest":
        return frappe.session.user

def get_batches(user):
    batch_names = frappe.db.get_all(
        "LMS Batch Membership",
        filters={"member": user, "member_type": "Mentor"},
        fields=["batch"],
        pluck="batch"
    )
    batches = [frappe.get_doc("LMS Batch", name) for name in batch_names]
    return batches

def select_batch(batches, batch_name):
    if not batch_name and batches:
        return batches[0]
    d = {b.name: b for b in batches}
    return d.get(batch_name)

def get_mentors(course_name, batch_name):
    """Returns (email, full_name, username) of all the students of this batch as a list of dict.
    """
    filters = {
        "course": course_name,
        "batch": batch_name,
        "member_type": "Mentor"
    }
    mentor_emails = frappe.get_all(
                "LMS Batch Membership",
                filters,
                ["member"],
                pluck="member")
    return [frappe.get_doc('User', email) for email in mentor_emails]

class BatchReport:
    def __init__(self, course, batch):
        self.course = course
        self.batch = batch
        self.submissions = get_submissions(course, batch)
        self.exercises = self.get_exercises(course.name)
        self.submissions_by_exercise = defaultdict(list)
        for s in self.submissions:
            self.submissions_by_exercise[s.exercise].append(s)

        self.students = course.get_students(batch.name)
        self.students_map = {s.email: s for s in self.students}

        self.lessons = self.course.get_lessons()

    def get_exercises(self, course_name):
        return frappe.get_all("Exercise", {"course": course_name, "lesson": ["!=", ""]}, ["name", "title", "lesson", "index_label"], order_by="index_label")

    def get_submissions_of_exercise(self, exercise_name):
        return self.submissions_by_exercise[exercise_name]

    def get_progress_by_lesson(self, lesson_name):
        count = sum(1 for e in self.exercises if e.lesson == lesson_name)
        counts_by_student = Counter(s.owner for s in self.submissions if s.lesson == lesson_name)

        print("progress", lesson_name, count, counts_by_student)
        value = sum(1 for v in counts_by_student.values() if v==count)

        return {
            "value": value,
            "count": len(self.students),
            "percent": self.percent(value, len(self.students))
        }
    def percent(self, value, count):
        if not count:
            return 0
        else:
            return value/count*100

    def get_progress_by_student(self):
        total = len(self.exercises)
        counts = Counter(s.owner.email for s in self.submissions)

        def progress(student):
            count = counts.get(student.email, 0)
            return {
                "student": student,
                "count": count,
                "total": total,
                "percent": self.percent(count, total)
            }

        return sorted([progress(s) for s in self.students], key=lambda p: p['count'], reverse=True)

def get_submissions(course, batch):
    students = course.get_students(batch.name)
    if not len(students):
        return []
    students_map = {s.email: s for s in students}
    values = {"batch": batch.name}
    sql = """
    select owner, exercise, lesson, batch, name, solution, creation, image
    from (
        select owner, exercise, lesson, batch, name, solution, creation, image,
            row_number() over (partition by owner, exercise order by creation desc) as ix
        from `tabExercise Submission`) as t
    where t.ix=1 and t.batch = %(batch)s
    """

    data = frappe.db.sql(sql, values=values, as_dict=True)
    for row in data:
        row['owner'] = students_map[row['owner']]
    return data
