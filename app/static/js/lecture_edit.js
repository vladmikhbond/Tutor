const content = document.getElementById("content");
const menu = document.getElementById("context-menu");

//#region --------------------- for confext menu ---------------------

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
//#endregion

//#region --------------------- for uploading picture --------------------

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

//#endregion

//#region --------------------- for replase '@' with emoji  --------------------

//               1    2    3     4    5     6
const MARKS = ['🔴','🔴','📔','❗','📗','📘']

content.addEventListener("keydown", (e) => {
  
  if (e.ctrlKey && 1 <= e.key && e.key <= 6) 
  {
    e.preventDefault();
    const index = content.selectionStart;
    if (content.value[index - 1] === '\n' || index == 0) {
      let mark = MARKS[e.key - 1] + e.key + " ";
      replaceString(content, mark, index)
    }
  }
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

//#endregion

//#region --------------------- for scroll after search -------------------

window.addEventListener('load', function (e) {
    let [_, start, end] = location.href.split("#");
    content.selectionStart = start;
    content.selectionEnd = end;
    content.focus();
    scrollTextareaToSelection(content)
});

// utility
//
function scrollTextareaToSelection(textarea) {
    const { selectionStart } = textarea;

    // Створюємо прихований елемент-дублер
    const div = document.createElement("div");
    const style = getComputedStyle(textarea);

    // Копіюємо стилі textarea → div
    for (const prop of style) {
        div.style[prop] = style[prop];
    }

    div.style.position = "absolute";
    div.style.visibility = "hidden";
    div.style.whiteSpace = "pre-wrap";
    div.style.overflow = "auto";
    div.style.height = "auto";

    // Текст до курсора + маркер
    const before = textarea.value.substring(0, selectionStart);
    const marker = document.createElement("span");
    marker.textContent = "█"; // маркер позиції
    marker.style.background = "yellow";

    div.textContent = before;
    div.appendChild(marker);

    document.body.appendChild(div);

    // Отримуємо позицію маркера
    const markerTop = marker.offsetTop;

    // Прокручуємо textarea так, щоб маркер був у видимій зоні
    textarea.scrollTop = markerTop - textarea.clientHeight / 2;

    document.body.removeChild(div);
}

//#endregion

//#region ---------------------- For Save Lection -----------------------------------------

// The '*' indices if the content.value changed.

buttonSave = document.getElementById("buttonSave");
asterisk = document.getElementById("asterisk");
edit_form = document.getElementById("edit_form");
lecture_id = document.getElementById("lecture_id");

content.addEventListener("keydown", (e) => {
  if (e.ctrlKey && (e.key == "s" || e.key == "S")) {
    e.preventDefault();
    saveLecture();
  }
})

buttonSave.addEventListener("click", e => {
    saveLecture();
})

content.addEventListener("input", function () {
  asterisk.innerHTML = "*";
});  

window.onbeforeunload = function (e) {
    if (asterisk.innerHTML == "*") {
        e.preventDefault();               
    }
};

async function saveLecture() {

  const data = new FormData(edit_form); 
  try 
  {
    const response = await fetch('/lecture/edit/' + lecture_id.value, {
      method: 'POST',
      body: data,
      credentials: 'include' // якщо потрібні кукі
    });
    if (!response.ok) {
      throw new Error(`Saving failed: ${response.status}`);
    }
  } 
  catch (err) 
  {
    alert(`Saving lecture error: ${err.message}`);
  }

  asterisk.innerHTML = "";
}

//#endregion

// Autosave in 3 min if text changed (IS OFF NOW)

// setInterval(function () {
//     if (! buttonSave.disabled)
//       document.getElementById("edit_form").submit();
//       buttonSave.disabled = true;
// }, 3 * 60000);