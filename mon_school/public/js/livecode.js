const LIVECODE_CODEMIRROR_OPTIONS = {
  lineNumbers: true,
  keyMap: "sublime",
  mode: "python",
  matchBrackets: true,
  indentWithTabs: false,
  tabSize: 4,
  indentUnit: 4,
  extraKeys: {
    Tab: (cm) => {
      cm.somethingSelected()
      ? cm.execCommand('indentMore')
      : cm.execCommand('insertSoftTab');
    }
  }
}

// Initialized the editor and all controls.
// It is expected that the given element is a parent element
// with textarea, div.output, button.run optionally canvas.canvas
// elements in it.
class LiveCodeEditor {
  constructor(element, options) {
    this.options = options;
    this.parent = element;

    this.base_url = options.base_url;
    this.runtime = options.runtime;

    this.files = options.files || [];
    this.env = options.env || {};
    this.command = options.command || null;

    this.elementCode = this.parent.querySelector(".code");
    this.elementOutput = this.parent.querySelector(".output");
    this.elementRun = this.parent.querySelector(".run");
    this.elementClear = this.parent.querySelector(".clear");
    this.elementReset = this.parent.querySelector(".reset");
    this.elementSVG = this.parent.querySelector(".svg-image svg");
    this.codemirror = null;
    this.autosaveTimeoutId = null;
    this.setupActions()
  }
  reset() {
    this.clearOutput();
    this.clearImage();
  }
  run() {
    this.triggerEvent("beforeRun");
    this.reset();
    this.runCode(this.getCode())
      .then((response) => {
        //console.log(response)
      });
  }
  runCode(code) {
    this.clearOutput();
    this.clearImage();

    return frappe.call({
      method: "mon_school.mon_school.livecode.execute",
      args: {
        code: code,
        is_sketch: false
      },
      success: ((data) => {
        const msg = data.message;
        this.writeOutput(msg.output.join(""));
        this.drawShapes(msg.shapes);
      })
    });
  }
  triggerEvent(name) {
      var events = this.options.events;
      if (events && events[name]) {
	      events[name](this);
      }
  }
  setupActions() {
    this.elementRun.onclick = () => this.run();
    if (this.elementClear) {
	    this.elementClear.onclick = () => this.triggerEvent("clear");
    }
    if (this.elementReset) {
	    this.elementReset.onclick = () => this.triggerEvent("reset");
    }

    if (this.options.codemirror) {
      const options = {
        ...LIVECODE_CODEMIRROR_OPTIONS,
      }
      if (this.options.codemirror instanceof Object) {
        options = {...options, ...this.options.codemirror}
      }
      options.extraKeys['Cmd-Enter'] = () => this.run()
      options.extraKeys['Ctrl-Enter'] = () => this.run()

      this.codemirror = CodeMirror.fromTextArea(this.elementCode, options)

      // if (this.options.autosave) {
      //   this.codemirror.on('change', (cm, change) => {
      //     if (this.autosaveTimeoutId) {
      //       clearTimeout(this.autosaveTimeoutId);
      //     }
      //     this.autosaveTimeoutId = setTimeout(() => {
      //       let code = this.codemirror.doc.getValue();
      //       this.options.autosave(this, code);
      //     }, 3000)
      //   })
      // }
    }
  }

  getCode() {
    if (this.codemirror) {
      var code = this.codemirror.doc.getValue()
      return code.replaceAll("\t", " ".repeat(this.codemirror.options.indentUnit))
    }
    else {
      return this.elementCode.value;
    }
  }

  clearOutput() {
    if (this.elementOutput) {
      this.elementOutput.innerHTML = "";
    }
  }
  clearImage() {
    if (this.elementSVG) {
      this.elementSVG.innerHTML = "";
    }
  }

  writeOutput(output_text) {
    // escape HTML
    var html = new Option(output_text).innerHTML;
    if (this.elementOutput) {
      this.elementOutput.innerHTML = html;
    }
  }
  drawShapes(shapes) {
    // const svgElement = editor.parent.querySelector("div.svg-image svg");
    this.elementSVG.innerHTML = "";
    shapes.forEach((s) => {
      this.elementSVG.innerHTML += this.renderShape(s);
    })
  }
  renderShape(shape) {
    var tag = shape.tag;
    var children = shape.children;
    var attrs = {...shape};
    delete attrs.tag;
    delete attrs.children;

    var svg = `<${tag}`
    Object.entries(attrs).forEach(([name, value]) => {
      name = name.replace("_", "-");
      svg += ` ${name}="${value}"`
    })

    if (children && children.length) {
      svg += ">\n"
      children.forEach(node => {
        svg += this.renderShape(node);
      })
      svg += `</${tag}>`;
    }
    else {
      svg += "/>";
    }
    return svg;
  }
}
