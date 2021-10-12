import frappe

def on_new_comment(doc, event_name):
    topic = frappe.get_doc("Discussion Topic", doc.topic)
    if topic.reference_doctype == "LMS Sketch":
        sketch = frappe.get_doc("LMS Sketch", topic.reference_docname)
        sketch.update_metrics()
