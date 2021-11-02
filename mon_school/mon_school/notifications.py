import frappe

def on_new_comment(doc, event_name):
    topic = frappe.get_doc("Discussion Topic", doc.topic)
    if topic.reference_doctype == "LMS Sketch":
        sketch = frappe.get_doc("LMS Sketch", topic.reference_docname)
        sketch.update_metrics()
        on_new_comment_on_sketch(sketch, doc)

def on_new_comment_on_sketch(sketch, discussion_reply):
    # No need to send notification for their own comments
    if sketch.owner == discussion_reply.owner:
        return

    author = frappe.get_doc("User", discussion_reply.owner)

    frappe.sendmail(
        recipients=[sketch.owner],
        subject="New Comment on Your Sketch",
        template="new-comment-on-sketch",
        args={
            "site_url": frappe.utils.get_url(),
            "sketch": sketch,
            "comment": discussion_reply.reply,
            "comment_author": author
        }
    )
