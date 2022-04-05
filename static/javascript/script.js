//Code credit: https://www.geeksforgeeks.org/how-to-insert-text-into-the-textarea-at-the-current-cursor-position/#:~:text=First%2C%20get%20the%20current%20position,and%20end%20of%20the%20text.
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