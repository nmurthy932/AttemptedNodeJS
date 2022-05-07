function deleteProject(id){
  var server_data = [
    {"docID": document.getElementById('url').href.split('/code/')[1]}
  ];
  $.ajax({
    type: "POST",
    url: "/delete-project",
    data: JSON.stringify(server_data),
    contentType: "application/json",
    dataType: 'json',
    success: function(result){
      document.getElementById(id).parentNode.parentNode.remove();
    }
  });
}