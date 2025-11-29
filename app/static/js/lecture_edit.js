//#region  ----------------------- utilities -------------------------


function replaceString(textArea, replaceStr, start, end) {
    if (end == undefined) 
      start = end;
    if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, replaceStr);
    } else {
      textArea.setSelectionRange(start, end);
      textArea.setRangeText(replaceStr, start, end, "select");
      textArea.dispatchEvent(new Event("input", { bubbles: true })); 
    }
}


function scrollTextareaToSelection(textArea) {
    const { selectionStart } = textArea;

    // Створюємо прихований елемент-дублер
    const div = document.createElement("div");
    const style = getComputedStyle(textArea);

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
    const before = textArea.value.substring(0, selectionStart);
    const marker = document.createElement("span");
    marker.textContent = "█"; // маркер позиції
    marker.style.background = "yellow";

    div.textContent = before;
    div.appendChild(marker);

    document.body.appendChild(div);

    // Отримуємо позицію маркера
    const markerTop = marker.offsetTop;

    // Прокручуємо textarea так, щоб маркер був у видимій зоні
    textArea.scrollTop = markerTop - textArea.clientHeight / 2;

    document.body.removeChild(div);
}

//#endregion

//#region --------------------- for confext menu ---------------------

const content = document.getElementById("content");
const menu = document.getElementById("context-menu");
const comment = document.getElementById("comment");

// Показати меню
content.addEventListener("contextmenu", e => {
  if (e.ctrlKey) {
    e.preventDefault();
    menu.style.display = "block";
    menu.style.left = e.pageX + "px";
    menu.style.top = e.pageY + "px";

    // Коригуємо позицію, якщо меню виходить за межі екрану
    const menuRect = menu.getBoundingClientRect();
    // Перевірка праворуч
    if (menuRect.right > window.innerWidth) {
      menu.style.left = (e.pageX - menuRect.width) + "px";
    }
    // Перевірка знизу
    if (menuRect.bottom > window.innerHeight) {
      menu.style.top = (e.pageY - menuRect.height) + "px";
    }
  }
});

// Приховати меню при кліку
content.addEventListener("click", () => {
  menu.style.display = "none";
});

comment.addEventListener("click", ()=> {
   const AA = "@@";

   let start = content.selectionStart, end = content.selectionEnd;
   let selected = content.value.slice(start, end);
   let lines = selected.split("\n");
   for (let i = 0; i < lines.length; i++) {
      if (lines[i].slice(0, AA.length) === AA)
          lines[i] = lines[i].slice(AA.length);
      else
          lines[i] = AA + lines[i];
   }
   let newSelected = lines.join("\n");
   replaceString(content, newSelected, start, end)
})

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

//#region --------------------- for insert emoji with ctrl key ------------

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

//#endregion

//#region --------------------- for scroll after search -------------------

window.addEventListener('load', function (e) {
    let [_, start, end] = location.href.split("#");
    content.selectionStart = start;
    content.selectionEnd = end;
    content.focus();
    scrollTextareaToSelection(content)
});

//#endregion

//#region --------------------- for save lection ---------------------------

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

//#region --------------------- toggle monospacing -------------------------

monoButton = document.getElementById("monoButton");

monoButton.addEventListener("click", () => {
  if (content.style.fontFamily !== "monospace") {
    content.style.fontFamily = "monospace";
  } else {
      content.style.fontFamily = "inherit";
  }       
});

//#endregion

// ----------------------- Autosave in 3 min if text changed (IS OFF NOW)

// setInterval(function () {
//     if (! buttonSave.disabled)
//       document.getElementById("edit_form").submit();
//       buttonSave.disabled = true;
// }, 3 * 60000);