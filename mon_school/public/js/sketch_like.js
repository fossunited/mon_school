var notLikedLikeIconSrc = "/assets/lms/icons/like.svg";
var likedLikeIconSrc = "/assets/mon_school/icons/red-like.svg";

function showLoginToLikeAlert() {
    // show alert for unauthenticated user
    frappe.show_alert({
      message: "Please login to like a sketch",
      indicator: "yellow",
    }, 5);
}

function toggleLike($btn) {
  if (!frappe.session.user || frappe.session.user == 'Guest') {
    console.log("unauthenticated user");

    showLoginToLikeAlert();
    return;
  }

  var sketchName = $btn.attr("data-sketch-name");
  var action = $btn.hasClass("not-liked") ? "like" : "unlike";

  frappe.call({
    method: "mon_school.mon_school.doctype.lms_sketch_like.lms_sketch_like.toggle_sketch_like",
    args: {
      sketch_name: sketchName,
      action: action,
    },
    btn: $btn, // disables button until a response is received
  })
  .then(r => {
    if (r.ok) {
      $likeIcon = $btn.find(".like-icon");
      $likeCount = $btn.find("#like-count");

      if (action == "like") {
        $btn.removeClass("not-liked").addClass("liked");
        $likeIcon.attr("src", likedLikeIconSrc);
        $likeCount.text(parseInt($likeCount.text()) + 1);
      } else if (action == "unlike") {
        $btn.removeClass("liked").addClass("not-liked");
        $likeIcon.attr("src", notLikedLikeIconSrc);
        $btn.find("#like-count")
        $likeCount.text(parseInt($likeCount.text()) - 1);
      }
    } else {
      var error = r.error;
      // log to console for now
      console.error(error);
    }
  })
}

$(document).ready(function(){
  $(".like-button").click(function(){
    toggleLike($(this));
  })
});
