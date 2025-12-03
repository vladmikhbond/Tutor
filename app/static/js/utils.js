// Замінює шматок тексту елементу <testarea>, який знах.між позиціями strt і end
//
function replaceString(textArea, replaceStr, start, end) 
{
    // Якщо end не визначено, вставка без заміни
    if (end === undefined) 
      end = start;
    
    // Встановлюємо виділення від start до end
    textArea.focus();
    textArea.setSelectionRange(start, end);

    // Спробуємо використати execCommand (краще для undo history)
    if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, replaceStr);
    } else {
      // Fallback: setRangeText замінює вибраний текст
      textArea.setRangeText(replaceStr, start, end, "end");
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


