window.onload = function () {
  var editor = CodeMirror.fromTextArea($("#code")[0], {
      lineNumbers: true,
      lineWrapping: true,
      mode: "javascript"
  });
  if(document.cookie.includes('teacher')){
    var editor2 = CodeMirror.fromTextArea($("#mkdown")[0], {
      lineNumbers: true,
      lineWrapping: true,
      mode: "markdown"
    });
    editor2.setSize('100%','95%');
    editor2.on('change',save);
  }
  editor.setSize('100%','95%');
  var output = document.getElementById('output');
  output.style.height = editor.getWrapperElement().offsetHeight;
  
  editor.on('change',save);

  switchTab('input');
  switchTab('console');

  if(window.location.href.split('#').length > 1){
    var urlEnd = window.location.href.split('#')[1];
    if(urlEnd == 'lesson'){
      $('#lesson').click();
    }
  }
};

function save(){
  var editor = document.getElementById('code').nextSibling.CodeMirror;
  code = editor.getValue();
  document.getElementById('save').textContent = 'Saving';
  if(document.cookie.includes('teacher')){
    var editor2 = document.getElementById('mkdown').nextSibling.CodeMirror;
    var markdownValue = editor2.getValue();
  }
  else{
    var markdownValue = '';
  }
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
        document.getElementById('title').textContent = document.getElementById('docName').value+' - LASAnode';
      else document.getElementById('title').textContent = 'Untitled project - LASAnode';
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
    if(document.cookie.includes('teacher')){
      var markdown = document.getElementById('markdownForm');
      var mdTab = document.getElementById('markdownEditTab');
    }
    var consolething = document.getElementById('codeForm');
    var consoleTab = document.getElementById('inputTab');
  }
  if(string == 'markdown' || (string == 'markdownEdit' && document.cookie.includes('teacher'))){
    consolething.style.display = 'none';
    markdown.style.display = 'block';
    mdTab.setAttribute('class','nav-link active');
    consoleTab.setAttribute('class','nav-link');
  }
  else if(string=='console' || string == 'input'){
    consolething.style.display = 'block';
    if(string == 'console' || document.cookie.includes('teacher')){
      markdown.style.display = 'none';
      mdTab.setAttribute('class','nav-link');
    }
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

function resizeOutput(){
  var editor = document.getElementById('code').nextSibling.CodeMirror;
  var output = document.getElementById('output');
  output.style.height = editor.getWrapperElement().offsetHeight;
}

function setSelectedLesson(id){
  if(document.cookie.includes('teacher')){
    var server_data = [
      {"lessonID": id},
      {"codeID": window.location.href.split('/code/')[1]}
    ];
    $.ajax({
      type: "POST",
      url: "/link-lesson",
      data: JSON.stringify(server_data),
      contentType: "application/json",
      dataType: 'json',
      success: function(result){
        console.log(id);
        document.getElementById('isLesson').style.display = 'inline-block';
        document.getElementById('isLesson2').style.display = 'inline-block';
        document.getElementById('newLessonForm').style.display = 'none';
        document.getElementById('isLesson2').childNodes[0].href = '/lessons/'+id+'/edit';
        document.getElementById('htmlTitle').textContent = result['title'];
        document.getElementById('htmlContent').innerHTML = result['content'];
      }
    });
  }
}

function removeSelectedLesson(){
  if(document.cookie.includes('teacher')){
    var server_data = [
      {"codeID": window.location.href.split('/code/')[1]},
      {"lessonID": document.getElementById('lessonIDStorage').value}
    ];
    $.ajax({
      type: "POST",
      url: "/unlink-lesson",
      data: JSON.stringify(server_data),
      contentType: "application/json",
      dataType: 'json',
      success: function(result){
        document.getElementById('isLesson').style.display = 'none';
        document.getElementById('isLesson2').style.display = 'none';
        document.getElementById('newLessonForm').style.display = 'inline-block';
        document.getElementById('htmlTitle').textContent = result['title']
        document.getElementById('htmlContent').innerHTML = result['html'];
      }
    });
  }
}

window.onresize = resizeOutput;