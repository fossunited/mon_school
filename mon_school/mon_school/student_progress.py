import sys
import frappe
from lms.lms.utils import get_lessons

class StudentProgress:
    """Progress of a student.
    """
    def __init__(self, course, email):
        self.email = email

        if isinstance(course, str):
            course = frappe.get_cached_doc("LMS Course", course)
        self.course = course

    def get_progress(self):
        lessons = get_lessons(self.course)
        lesson_dict = {lesson.name: lesson for lesson in lessons}

        exercises = frappe.get_all("LMS Exercise", filters={"course": self.course.name}, fields=["name", "lesson", "index_label"])
        submissions = frappe.get_all("Exercise Latest Submission",
            filters={"course": self.course.name, "member_email": self.email},
            fields=["*"])
        self.submissions_dict = {s.exercise: s for s in submissions}

        for lesson in lessons:
            lesson.exercises = []

        for e in exercises:
            if e.lesson:
                lesson_dict[e.lesson].exercises.append(e)

        return {
            "lessons": [self.prepare_lesson(lesson) for lesson in lessons]
        }

    def prepare_exercise(self, e):
        title = f"E{e.index_label}"
        complete = e.name in self.submissions_dict
        return dict(title=title, complete=complete)

    def prepare_lesson(self, lesson):
        return {
            "title": f"{lesson.number}. {lesson.title}",
            "url": f"/courses/{self.course.name}/learn/{lesson.number}",
            "complete": False,
            "chapter": int(lesson.number),
            "number": lesson.number,
            "exercises": [self.prepare_exercise(e) for e in lesson.exercises]
        }
