window.livecode.template = `
<div class="livecode-editor">
  <div class="filenames" id="file-tabs">

  <div class="pull-right labels hidden"></div>
  </div>

  <div class="code-editor">
    <div class="code-wrapper">
      <textarea class="code"></textarea>
    </div>

    <div class="controls">
    <span class="run-args-label hidden">Arguments: &nbsp;</span>
    <input type="text" class="run-args hidden" name="args" value="" placeholder=""/>
    <div class="run-wrapper">
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
    </div>
  </div>
</div>
`;
