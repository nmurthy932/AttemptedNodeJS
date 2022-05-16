function save(){
  if(document.cookie.includes('teacher')){
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
            else document.getElementById('title').textContent = 'Untitled project - LASAnode';
            document.getElementById('content').innerHTML = result['processed'];
        }
    });
  }
}

function deleteProject(){
  if(document.cookie.includes('teacher')){
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
            window.location.replace(result['processed']);
        }
    });
  }
}

window.onload = function () {
  if(document.cookie.includes('teacher')){
    var editor = CodeMirror.fromTextArea($("#textarea")[0], {
        lineNumbers: true,
        lineWrapping: true,
        mode: "xml",
        htmlMode: true
    });
    editor.setSize('100%','97%');
    editor.on('change',save);
    document.getElementById('output').style.height = editor.getWrapperElement().offsetHeight;
    document.getElementById('content').innerHTML = editor.getValue();
  }
};

  $('#codeForm').on('keyup keypress', function(e) {
    if(document.cookie.includes('teacher')){
      var keyCode = e.keyCode || e.which;
      if (keyCode === 13 && !$(document.activeElement).is('textarea')) {
        e.preventDefault();
        return false;
      }
    }
  });

  function resizeOutput(){
    if(document.cookie.includes('teacher')){
      var editor = document.getElementById('textarea').nextSibling.CodeMirror;
      var output = document.getElementById('output');
      output.style.height = editor.getWrapperElement().offsetHeight;
    }
  }

  function setSelectedLesson(id){
    if(document.cookie.includes('teacher')){
      var server_data = [
        {"lessonID": window.location.href.split('/lessons/')[1].split('/edit')[0]},
        {"codeID": id}
      ];
      $.ajax({
        type: "POST",
        url: "/link-lesson",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
            window.location.reload();
        }
      });
    }
  }
  
  function removeSelectedLesson(id){
    if(document.cookie.includes('teacher')){
      var server_data = [
        {"codeID": id},
        {"lessonID": window.location.href.split('/lessons/')[1].split('/edit')[0]}
      ];
      $.ajax({
        type: "POST",
        url: "/unlink-lesson",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
          window.location.reload();
        }
      });
    }
  }

  function publish(){
    if(document.cookie.includes('teacher')){
      var server_data = [
        {'document': 'lesson'},
        {'lessonID': window.location.href.split('/lessons/')[1].split('/edit')[0]},
        {'published': document.getElementById('published').checked}
      ]
      $.ajax({
        type: "POST",
        url: "/set-published",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
          if(document.getElementById('published').checked){
            $('label[for="published"]').text('Published');
          }
          else{
            $('label[for="published"]').text('Unpublished');
          }
        }
      });
    }
  }
  
  window.onresize = resizeOutput;