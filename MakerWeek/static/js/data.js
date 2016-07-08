var codeArea = CodeMirror.fromTextArea(document.getElementById("code-area"), {
    mode: "text/x-mariadb",
    lineWrapping: true,
    autofocus: true,
    theme: "monokai",
    lineNumbers: true,
});