"""Global context for templates injected by Mon School.

Adds a variable `monschool` to the context, which is an instance of
MonSchool containing all the utilities provided by the Mon School app.
"""
import frappe

def update_website_context(context):
    context.monschool = MonSchool()

class MonSchool:
    """Utilities to use in templates from monschool.

    If you want to include a function to be available to all the templates,
    including the web templates, add it here.
    """
    def ping(self):
        return "pong"

    def get_num_students(self, cohort_name, subgroup_name=None):
        filters = {"cohort": cohort_name}
        if subgroup_name:
            filters["subgroup"] = subgroup_name

        return frappe.db.get_value(
            "LMS Batch Membership",
            filters=filters,
            fieldname="count(*) as count")

    def get_exercises_in_course(self, course):
        """Returns all the exercises in the course as a dict with exercise name as the key and other details as value.
        """
        d = frappe.get_all("Exercise",
                filters={"course": course},
                fields=["name", "title", "index_label"],
                page_length=1000)

        d = [row for row in d if row.index_label]

        def index_value(e):
            a, b = e['index_label'].split(".")
            return int(a), int(b)
        return sorted(d, key=index_value)

    def get_exercise_submission_counts(self, cohort_name, subgroup_name=None):
        filters = {"member_cohort": cohort_name}
        if subgroup_name:
            filters["member_subgroup"] = subgroup_name

        rows = frappe.get_all("Exercise Latest Submission",
            filters=filters,
            fields=["exercise", "count(*) as count"],
            group_by="1",
            order_by="2 desc",
            page_length=1000)
        return {row.exercise: row.count for row in rows}

    def get_progress_by_exercise(self, course, cohort_slug, subgroup_slug=None):
        """Returns the progress by exercise in a cohort.
        """
        cohort_name = f"{course}/{cohort_slug}"
        subgroup_name = subgroup_slug and frappe.get_cached_doc("Cohort", cohort_name).get_subgroup(subgroup_slug).name

        num_students = self.get_num_students(cohort_name, subgroup_name)
        if num_students == 0:
            return []

        counts = self.get_exercise_submission_counts(cohort_name, subgroup_name)
        exercises = self.get_exercises_in_course(course)
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

