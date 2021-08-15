import frappe


def get_context(context):
    context.no_cache = 1

    try:
        contest_name = frappe.form_dict["contest"]
    except KeyError:
        context.template = "www/404.html"
        return


    try:
        sketch_name = frappe.form_dict["sketch"]
    except KeyError:
        context.template = "www/404.html"
        return

    try:
        contest = frappe.get_doc("Contest", contest_name)
    except frappe.DoesNotExistError:
        context.template = "www/404.html"
        return

    sketch = contest.get_submission(sketch_name)

    if not sketch:
        context.template = "www/404.html"
        return

    context.contest = contest
    context.sketch = sketch
    context.page_context = {}
    context.metatags = get_metatags(sketch)

def get_metatags(sketch):
    title = f"{sketch.title}  by {sketch.get_owner_name()}"
    image = sketch.get_image_url(mode="w")
    url = f"{frappe.request.host_url}sketches/{sketch.sketch_id}"
    return {
        "title": title,
        "description": sketch.code,
        "image": image,
        "url": url
    }
