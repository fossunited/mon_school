// Live Code integration for the joy-of-programming course
function setupJoy() {
  var editorLookup = {};

  var template = `
  <div class="livecode-editor livecode-editor-inline">
    <div class="code-editor">
      <div class="code-wrapper">
        <textarea class="code"></textarea>
      </div>
    </div>
    <div class="controls">
      <div class="exercise-controls">
        <button class="submit button btn-primary">Submit Solution</button>
        <!-- <div style="padding-right: 10px;"><span class="last-submitted human-time" data-timestamp=""></span></div> -->
      </div>
      <div class="run-wrapper" style="display: inline;">
        <button class="run button">Run Code</button>
        <span class="run-status"></span>
      </div>
    </div>

    <div class="output-bar">
      <button class="collapse-button button tiny-button pull-right expanded">- Collapse</button>
      <span class="output-label">Output</span>
    </div>
    <div class="output-wrapper">
      <pre class="output"></pre>
      <div class="canvas-wrapper">
        <div class="svg-image" width="300" height="300">
          <svg width="300" height="300" viewBox="-150 -150 300 300" fill="none" stroke="black" xmlns="http://www.w3.org/2000/svg">
          </svg>
        </div>
      </div>
    </div>
  </div>
  `;

  if ('is_member' in page_context && !page_context.is_member) {
    $("pre.exercise").replaceWith('<div class="alert alert-warning">Please join the course to submit exercises.</div>')
  }

  $("pre.example, pre.exercise").each((i, e) => {
    var code;

    if ($(e).hasClass("exercise")) {
      code = JSON.parse($(e).data("code")).trimEnd();
    }
    else {
      code = $(e).text().trimEnd();
    }

    var context = {
      ...page_context
    }

    $(e)
    .wrap('<div style="width: 100%;"></div>')
    .hide()
    .parent()
    .append(template)
    .find("textarea.code")
    .val(code);

    if ($(e).hasClass("exercise")) {
      context.source_type = "exercise";
      context.exercise = $(e).data("name");

      var last_submitted = $(e).data("last-submitted");
      if (last_submitted) {
        $(e).parent().find(".last-submitted")
          .data("timestamp", last_submitted)
          .html(__("Submitted {0}", [comment_when(last_submitted)]));
      }
    }
    else {
      context.source_type = "example";
      context.example = $(e).attr("id");

      $(e).parent().find(".exercise-controls").remove();
    }

    var editor = new LiveCodeEditor(e.parentElement, {
      codemirror: true,
      context: context,
      events: {
        beforeRun: function() {
          expandOutput(editor.parent);
        }
      }
    });

    $(e).parent().find(".submit").on('click', function() {
      var name = $(e).data("name");
      let code = editor.codemirror.doc.getValue();

      frappe.call("school.lms.api.submit_solution", {
        "exercise": name,
        "code": code
      }).then(r => {
        if (r.message.name) {
          frappe.msgprint("Submitted successfully!");

          let d = r.message.creation;
          $(e).parent().find(".human-time").html(__("Submitted {0}", [comment_when(d)]));
        }
      });
    });
  });

  $(".exercise-image").each((i, e) => {
    var svg = JSON.parse($(e).data("image"));
    $(e).html(svg);

    // hide the image if it is empty
    if ($(e).find("svg").children().length == 0) {
      $(e).hide();
    }
  });

  $("pre.example").each((i, e) => {
    collapseOutput($(e).parent());
    $(e).parent().find(".output-bar").hide();
  });

  $("pre.exercise").each((i, e) => {
    var svg = JSON.parse($(e).data("image"));
    if (svg) {
      // We need to add the svg without removing the svg element from DOM
      // as the <svg> element is already cached in the LiveCodeEditor.
      //
      // We are adding the svg to a temporary div and taking the innerHTML
      // of the svg element and copying that to the svg element already
      // present in the DOM.
      var div = document.createElement("div");
      div.innerHTML = svg;

      var innerSVG = $(div).find("svg").html();
      $(e).parent().find(".svg-image svg").html(innerSVG);
      expandOutput($(e).parent());
    }

    // XXX: The livecode editor wasn't showing full width for exercises
    // This is a hack to fix it
    $(e).closest("div.exercise").parent().attr("style", "width: 100%;")
  });

  $(".collapse-button").on('click', function() {
    const e = $(this).closest(".livecode-editor");

    if ($(this).hasClass("collapsed")) {
      expandOutput(e);
    }
    else {
      collapseOutput(e);
    }
  });

  function expandOutput(livecode_element) {
    $(livecode_element)
      .find(".collapse-button")
      .text("- Collapse")
      .removeClass("collapsed");

    $(livecode_element).find(".output-bar").show();
    $(livecode_element).find(".output-wrapper").show();
  }

  function collapseOutput(livecode_element) {
    $(livecode_element)
      .find(".collapse-button")
      .text("+ Expand")
      .addClass("collapsed");

    $(livecode_element).find(".output-wrapper").hide();
  }

  if (document.location.hash) {
    var h = document.location.hash.replace("#", "");
    var e = document.getElementById(h);
    if (e) {
      e.scrollIntoView();
    }
  }

  $(".widget").each(function(i, e) {
    var t = JSON.parse($(e).data('template'));
    $(e).html(t);
  });
}

window.setupJoy = setupJoy
