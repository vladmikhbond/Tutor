const content = document.getElementById("content");
const menu = document.getElementById("context-menu");

// ----------------- confext menu ---------------------

// Показати меню
content.addEventListener("contextmenu", e => {
  if (e.ctrlKey) {
    e.preventDefault();
    menu.style.display = "block";
    menu.style.left = e.pageX + "px";
    menu.style.top = e.pageY + "px";
  }
});

// Приховати меню при кліку
content.addEventListener("click", () => {
  menu.style.display = "none";
});

// --------------------- upload picture --------------------

const upload_form = document.getElementById("upload_form")

upload_form.addEventListener("submit", async (e) => {
  e.preventDefault();

  
  // Create a formdata object and add the files
  let data = new FormData();
  let files = document.getElementById('file').files;
  if (files && files.length) {
      data.append('file', files[0]);
  }
  // const data = new FormData(upload_form);  // а це чомусь не працює !?

  const disc_id = document.getElementById("disc_id");  
  data.append('disc_id', disc_id.value);
  try 
  {
    const response = await fetch('/lecture/picture', {
      method: 'POST',
      body: data,
      credentials: 'include' // якщо потрібні кукі
    });
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    let answer = await response.json();
    let i =  content.selectionStart;
    let txt = content.value.substr(0, i) + '[[' + answer.filename + ']]' + content.value.substr(i);
    content.value = txt;
  } 
  catch (err) 
  {
    alert(`Upload error: ${err.message}`);
  }
});

// ---------------------  --------------------

let ctrl_pressed = false;
//               1    2    3     4    5     6
const MARKS = ['🔴','🔴','📔','❗','📗','📘']

content.addEventListener("keydown", (e) => {
    
    if (ctrl_pressed) {
      e.preventDefault();
      const index = content.selectionStart;
      if (1 <= e.key && e.key <= 6) {
        if (content.value[index - 1] === '\n' || index == 0) {
          let mark = MARKS[e.key - 1] + e.key + " ";
          replaceString(content, mark, index)
        }
      }
    }
    ctrl_pressed = e.key == "Control";
})

function replaceString(ta, replaceStr, start, end) {
    if (end == undefined) 
      start = end;
    if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, replaceStr);
    } else {
      ta.setSelectionRange(start, end);
      ta.setRangeText(replaceStr, start, end, "select");
      ta.dispatchEvent(new Event("input", { bubbles: true })); 
    }
}