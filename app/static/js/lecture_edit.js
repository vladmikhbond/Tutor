const content = document.getElementById("content");

//#region --------------------- for Play link ---------------------

document.getElementById("playLink").addEventListener("click", (e) => {
  e.preventDefault();

  // calculate slide nomber
  const caretPos = content.selectionStart;
  const str = content.value.slice(0, caretPos);
  const slide_no = [...str].reduce((n, ch) => n + MARKS.includes(ch), 0) - 1;
  // 
  const lecture_id = document.getElementById("lecture_id").value;
  window.location.href = `/lecture/trans/${lecture_id}?slide_no=${slide_no}`;
});

//#endregion

//#region --------------------- for confext menu ---------------------

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
   const AA = "@@ ";

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
  if (e.ctrlKey && (e.key == "s" || e.key == "S" || e.key == "і" || e.key == "І")) {
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

//#region --------------------- legacy converter -------------------------

const legacyButton = document.getElementById("legacуButton");

legacyButton.addEventListener("click", (e) => {
  e.preventDefault();
  newValue = content.value.replaceAll("@1", '🔴1').replaceAll("@2", '🔴2').replaceAll("@3", '📔3')
      .replaceAll("@4", '❗4').replaceAll("@5", '📘5');  
  replaceString(content, newValue, 0, content.value.length)
});

//#endregion



// ----------------------- Autosave in 3 min if text changed (IS OFF NOW)

// setInterval(function () {
//     if (! buttonSave.disabled)
//       document.getElementById("edit_form").submit();
//       buttonSave.disabled = true;
// }, 3 * 60000);