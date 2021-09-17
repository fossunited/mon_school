import frappe
from mon_school.mon_school.doctype.lms_sketch.lms_sketch import LMSSketch as Sketch

def get_context(context):
    context.no_cache = 1

    limit = get_limit()
    context.sketches = Sketch.get_recent_sketches(limit=limit)

def get_limit(default=48):
    try:
        value = frappe.form_dict.get("limit", default)
        limit = int(value)
        return bound(limit, min_value=default, max_value=1000)
    except ValueError:
        return default

def bound(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value
