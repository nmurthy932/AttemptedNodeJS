window.onload = function () {
  var editor = CodeMirror.fromTextArea($("#code")[0], {
      lineNumbers: true,
      lineWrapping: true,
      mode: "javascript"
  });
  var editor2 = CodeMirror.fromTextArea($("#mkdown")[0], {
    lineNumbers: true,
    lineWrapping: true,
    mode: "markdown"
  });
  editor.setSize('100%','95%');
  editor2.setSize('100%','95%');
  var output = document.getElementById('output');
  output.style.height = editor.getWrapperElement().offsetHeight;
  code = editor.getValue();
  
  editor.on('change',save);
  editor2.on('change',save);
};

function save(){
  var editor = document.getElementById('code').nextSibling.CodeMirror;
  code = editor.getValue();
  document.getElementById('save').textContent = 'Saving';
  var editor2 = document.getElementById('mkdown').nextSibling.CodeMirror;
  var markdownValue = editor2.getValue();
  var server_data = [
    {"Name": document.getElementById('docName').value},
    {"docID": window.location.href.split('/code/')[1]},
    {"code": code},
    {"markdown": markdownValue}
  ];
  $.ajax({
    type: "POST",
    url: "/update-code",
    data: JSON.stringify(server_data),
    contentType: "application/json",
    dataType: 'json',
    success: function(result){
      document.getElementById('save').textContent = 'Saved';
      if(document.getElementById('docName').value != '')
        document.getElementById('title').textContent = document.getElementById('docName').value;
      else document.getElementById('title').textContent = 'Untitled project';
      createMarkdown(markdownValue);
    }
  });
}

function setOutputStyle(){
  output.setAttribute('overflow-y','auto');
  output.style.margin = "10px";
  output.style.border = "border: 1px solid black;";
}

function runCode(){
  save();
  document.getElementById('codeForm').submit();
}

function switchTab(string){
  if(string == 'markdown' || string == 'console'){
    var markdown = document.getElementById('markdown');
    var consolething = document.getElementById('console');
    var mdTab = document.getElementById('markdownTab');
    var consoleTab = document.getElementById('consoleTab');
  }
  else{
    var markdown = document.getElementById('markdownForm');
    var consolething = document.getElementById('codeForm');
    var mdTab = document.getElementById('markdownEditTab');
    var consoleTab = document.getElementById('inputTab');
  }
  if(string == 'markdown' || string == 'markdownEdit'){
    consolething.style.display = 'none';
    markdown.style.display = 'block';
    mdTab.setAttribute('class','nav-link active');
    consoleTab.setAttribute('class','nav-link');
  }
  else if(string=='console' || string == 'input'){
    consolething.style.display = 'block';
    markdown.style.display = 'none';
    mdTab.setAttribute('class','nav-link');
    consoleTab.setAttribute('class','nav-link active');
  }
}

$('#codeForm').on('keyup keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13 && !$(document.activeElement).is('textarea')) {
    e.preventDefault();
    return false;
  }
});

function createMarkdown(string){
  var md = window.markdownit();
  var result = md.render(string);
  $('#markdown').html(result);
}