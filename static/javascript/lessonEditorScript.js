function save(){
    var editor = document.getElementById('textarea').nextSibling.CodeMirror;
    code = editor.getValue();
    document.getElementById('save').textContent = 'Saving';
    var server_data = [
        {"title": document.getElementById('lessonName').value},
        {"docID": window.location.href.split('/lessons/')[1].split('/edit')[0]},
        {"content": code}
    ];
    $.ajax({
        type: "POST",
        url: "/update-lesson",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
            document.getElementById('save').textContent = 'Saved';
            if(document.getElementById('lessonName').value != '')
                document.getElementById('title').textContent = document.getElementById('lessonName').value+" - LASAnode";
            else document.getElementById('title').textContent = 'Untitled project';
            document.getElementById('content').innerHTML = result['processed'];
        }
    });
}

function deleteProject(){
    var server_data = [
        {"docID": window.location.href.split('/lessons/')[1].split('/edit')[0]}
    ];
    $.ajax({
        type: "POST",
        url: "/delete-lesson",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
            console.log(result)
            window.location.replace(result['processed']);
        }
    });
}

window.onload = function () {
    var editor = CodeMirror.fromTextArea($("#textarea")[0], {
        lineNumbers: true,
        lineWrapping: true,
        mode: "xml",
        htmlMode: true
    });
    editor.setSize('100%','95%');
    editor.on('change',save);
    document.getElementById('output').style.height = editor.getWrapperElement().offsetHeight;
    document.getElementById('content').innerHTML = editor.getValue();
  };

  $('#codeForm').on('keyup keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13 && !$(document.activeElement).is('textarea')) {
      e.preventDefault();
      return false;
    }
  });

  function resizeOutput(){
    var editor = document.getElementById('textarea').nextSibling.CodeMirror;
    var output = document.getElementById('output');
    output.style.height = editor.getWrapperElement().offsetHeight;
  }
  
  window.onresize = resizeOutput;