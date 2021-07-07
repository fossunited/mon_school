import frappe

def get_context(context):
    context.no_cache = 1
    context.user = get_user()
    context.memberships = get_memberships(context.user)

def get_user():
    if frappe.session.user != "Guest":
        return frappe.session.user

def get_memberships(user):
    memberships = frappe.db.get_all(
        "LMS Batch Membership",
        filters={"member": user},
        fields=["name", "batch", "course", "member_type"]
    )
    return [load_membership(row) for row in memberships]

def load_membership(row):
    batch = row.batch and frappe.get_doc("LMS Batch", row.batch)

    # some legacy records have course as null.
    # hoping that both the batch and the course will never be None.
    if row.course == None:
        row.course = batch and batch.course

    return {
        "member_type": row.member_type,
        "batch": batch,
        "course": frappe.get_doc("LMS Course", row.course)
    }