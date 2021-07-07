import frappe
from mon_school.mon_school.doctype.lms_sketch.lms_sketch import LMSSketch as Sketch

def get_context(context):
    context.no_cache = 1
    context.sketches = Sketch.get_recent_sketches()

