
function override(path, callback) {
  const re = new RegExp(path);
  const match = window.location.pathname.match(re);
  if (match != null) {
    callback.apply(this, match.slice(1));
  }
}

$(function() {
  const SIGNED_UP_TITLE = "&#10004; You've signed up for early access";


  function hasSignedUpForEarlyAccess() {
    return $("#notify-me").attr("disabled") == "disabled";
  }

  function markAsSignedUp() {
    $("#notify-me").attr("disabled", "disabled");
    updateEarlyAccessButton()
  }

  function updateEarlyAccessButton() {
    const b = $("#signup-for-early-access")
    if (hasSignedUpForEarlyAccess()) {
      b.html(SIGNED_UP_TITLE);
      b.attr("disabled", "disabled");
    }
    else {
      b.html("Signup for early access");
      b.attr("disabled", null);
    }
  }

  override("/courses/([^/]*)", (course) => {
    if ($("#notify-me").length) {
      $("#notify-me").hide();

      var b = $("<button></button>")
        .appendTo(".course-buttons")
        .attr("id", "signup-for-early-access")
        .html("Sign up for early acces")
        .addClass("button wide-button is-default")
        .click(function(e) {
          e.preventDefault();
          signup_for_early_access(course);
       });
      updateEarlyAccessButton();
    }
  });


  var signup_for_early_access = (course) => {
    if (frappe.session.user == "Guest") {
      window.location.href = `/mon/signup_for_early_access?course=${course}`;
      return;
    }

    frappe.call({
      method: "lms.lms.doctype.lms_course_interest.lms_course_interest.capture_interest",
      args: {
        "course": course
      },
      callback: (data) => {
        frappe.msgprint({
          title: __("Thank you!"),
          indicator: "green",
          message:  "We'll notify you via email when the course is ready for preview."
        });
        markAsSignedUp();
      }
    });
  }
});
