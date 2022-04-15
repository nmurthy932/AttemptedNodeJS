function deleteProject(docID, id){
  var server_data = [
    {"docID": docID}
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