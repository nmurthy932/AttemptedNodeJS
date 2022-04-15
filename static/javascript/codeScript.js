//Code credit: https://www.geeksforgeeks.org/how-to-insert-text-into-the-textarea-at-the-current-cursor-position/#:~:text=First%2C%20get%20the%20current%20position,and%20end%20of%20the%20text.
/*
document.getElementById('code').addEventListener('keydown', function (e) {
  if(e.keyCode==9) {
    console.log('GOT HERE');
    e.preventDefault();
    let x = $("#code").val();
    let curPos = e.target.selectionStart;
    $("#code").val(
x.slice(0, curPos) + '\t' + x.slice(curPos));
  }
})
*/

window.onload = function () {
  var editor = CodeMirror.fromTextArea($("#code")[0], {
      lineNumbers: true,
      lineWrapping: true,
      mode: "javascript",
  });
  editor.setSize('100%','95%');
  var output = document.getElementById('output');
  output.style.height = editor.getWrapperElement().offsetHeight;
};

function setOutputStyle(){
  output.setAttribute('overflow-y','auto');
  output.style.margin = "10px";
  output.style.border = "border: 1px solid black;";
}

function runCode(){
  document.getElementById('codeForm').submit();
}

function createMarkdown(string){
  var md = window.markdownit();
  var result = md.render(string);
  $('#markdown').html(result);
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