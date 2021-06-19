import frappe

def get_context(context):
    context.no_cache = 1
    context.user = get_user()
    context.batches = get_batches(context.user)

def get_user():
    if frappe.session.user != "Guest":
        return frappe.session.user

def get_batches(user):
    batch_names = frappe.db.get_all(
        "LMS Batch Membership",
        filters={"member": user},
        fields=["batch"],
        pluck="batch"
    )
    batches = [frappe.get_doc("LMS Batch", name) for name in batch_names]
    return batches