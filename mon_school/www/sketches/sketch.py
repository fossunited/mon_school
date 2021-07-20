import frappe

def get_context(context):
    context.no_cache = 1

    try:
        sketch_id = frappe.form_dict["sketch"]
    except KeyError:
        context.template = "www/404.html"
        return

    sketch = get_sketch(sketch_id)
    if not sketch:
        context.template = "www/404.html"
        return

    context.sketch = sketch
    context.livecode_url = get_livecode_url()
    context.editable = is_editable(context.sketch, frappe.session.user)

    context.page_context = {
        "source_type": "sketch",
        "sketch": sketch.name
    }

    context.metatags = get_metatags(sketch)

def get_metatags(sketch):
    image = f"{frappe.request.host_url}s/{sketch.sketch_id}.png"
    url = f"{frappe.request.host_url}sketches/{sketch.sketch_id}"
    return {
        "title": sketch.title,
        "description": sketch.code,
        "image": image,
        "url": url
    }

def is_editable(sketch, user):
    if sketch.is_new():
        # new sketches can be editable by any logged in user
        return user != "Guest"
    else:
        # existing sketches are editable by the owner
        return sketch.owner == user

def get_livecode_url():
    doc = frappe.get_doc("LMS Settings")
    return doc.livecode_url

def get_sketch(sketch_id):
    if sketch_id == 'new':
        sketch = frappe.new_doc('LMS Sketch')
        sketch.name = ""
        sketch.title = "New Sketch"
        sketch.code = "c = circle()\nshow(c)"
        return sketch

    try:
        name = "SKETCH-" + sketch_id
        return frappe.get_doc('LMS Sketch', name)
    except frappe.exceptions.DoesNotExistError:
        return

