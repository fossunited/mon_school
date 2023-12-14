# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version
from .install import APP_LOGO_URL

app_name = "mon_school"
app_title = "Mon School"
app_publisher = "FOSS United"
app_description = "Frappe App for Mon School branding"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "anand@fossunited.org"
app_license = "MIT"

app_logo_url = APP_LOGO_URL

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mon_school/css/mon_school.css"
# app_include_js = "/assets/mon_school/js/mon_school.js"

# include js, css files in header of web template
web_include_css = "mon_school.bundle.css"
web_include_js = "mon_school.bundle.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mon_school/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "mon_school.install.before_install"
after_install = "mon_school.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mon_school.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

override_doctype_class = {
	"LMS Exercise": "mon_school.mon_school.overrides.LMSExercise",
	"Exercise Submission": "mon_school.mon_school.overrides.ExerciseSubmission",
	"LMS Batch Membership": "mon_school.mon_school.overrides.LMSBatchMembership",
	"Cohort": "mon_school.mon_school.overrides.Cohort",
	"Cohort Subgroup": "mon_school.mon_school.overrides.CohortSubgroup",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Discussion Reply": {
        "on_update": "mon_school.mon_school.notifications.on_new_comment"
    }
}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"mon_school.tasks.all"
# 	],
# 	"daily": [
# 		"mon_school.tasks.daily"
# 	],
# 	"hourly": [
# 		"mon_school.tasks.hourly"
# 	],
# 	"weekly": [
# 		"mon_school.tasks.weekly"
# 	]
# 	"monthly": [
# 		"mon_school.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "mon_school.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mon_school.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "mon_school.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Profile Tabs
profile_tabs = [
	"mon_school.mon_school.plugins.SketchesTab"
]

lms_lesson_page_extensions = [
	"mon_school.mon_school.plugins.LiveCodeExtension"
]

website_route_rules = [
  {"from_route": "/<contest>/submissions", "to_route": "contest_sketches/index"},
  {"from_route": "/<contest>/review", "to_route": "contest_sketches/review"},
  {"from_route": "/<contest>/submissions/edit", "to_route": "contest_sketches/edit"},
  {"from_route": "/<contest>/submissions/<sketch>", "to_route": "contest_sketches/view"}
]

signup_form_template = "mon_school/templates/signup_form.html"

update_website_context = [
    'mon_school.mon_school.context.update_website_context',
]

lms_markdown_macro_renderers = {
	"Exercise": "mon_school.mon_school.plugins.exercise_renderer",
	"Image": "mon_school.mon_school.plugins.image_renderer",
	"YouTubeVideo": "mon_school.mon_school.plugins.youtube_video_renderer",
	"Widget": "mon_school.mon_school.plugins.widget_renderer",
	"Task": "mon_school.mon_school.plugins.task_renderer",
}

# Install custom page renderers
from mon_school.mon_school.page_renderers import page_renderer as _page_renderer
page_renderer = _page_renderer

profile_url_prefix = "/"
