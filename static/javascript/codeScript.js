//Code credit: https://www.geeksforgeeks.org/how-to-insert-text-into-the-textarea-at-the-current-cursor-position/#:~:text=First%2C%20get%20the%20current%20position,and%20end%20of%20the%20text.

window.onload = function () {
  var editor = CodeMirror.fromTextArea($("#code")[0], {
      lineNumbers: true,
      lineWrapping: true,
      mode: "javascript",
  });
  editor.setSize('100%','95%');
  var output = document.getElementById('output');
  output.style.height = editor.getWrapperElement().offsetHeight;
  code = editor.getValue();
  
  editor.on('change',save);
};

function save(){
  var editor = document.getElementById('code').nextSibling.CodeMirror;
  code = editor.getValue();
  document.getElementById('save').textContent = 'Saving';
  var server_data = [
    {"Name": document.getElementById('docName').value},
    {"docID": window.location.href.split('/code/')[1]},
    {"code": code}
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
  var md = document.getElementById('markdown');
  var console = document.getElementById('console');
  var mdTab = document.getElementById('markdownTab');
  var consoleTab = document.getElementById('consoleTab')
  if(string == 'markdown'){
    console.style.display = 'none';
    markdown.style.display = 'inline-block';
    mdTab.setAttribute('class','nav-link active');
    consoleTab.setAttribute('class','nav-link');
  }
  else{
    console.style.display = 'inline-block';
    markdown.style.display = 'none';
    mdTab.setAttribute('class','nav-link');
    consoleTab.setAttribute('class','nav-link active');
  }
}