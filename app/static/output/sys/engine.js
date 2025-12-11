/* цей файл має знаходитися у папці sys */

// ---------------------- Параметри рендерінгу (визначені на сторінці)-----------------------
// const START_SLIDE_NO={slide_no}; 
// const VERSION = "{self.version}";
// const LIGHT_COLORS = {"page-bg": "#edf2f8", "header": "#0000ff", "text": "#000080", "bg": "#e6eef5", "link": "#d3589b"}
const DARK_COLORS = {"page-bg": "#666", "header": "#aaaaff", "text": "#fff", "bg": "#444", "link": "#d3589b"}

// ------------------------------- globals ------------------------------------------

let current_slide_no = START_SLIDE_NO; // номер сфокусованого слйду
let slides = document.querySelectorAll("#lecture > div");
let theme = "light";

setColors(LIGHT_COLORS);
go(0);

// ----------------------- перемикач світлої і темної тем --------------------------

function setRootVar(name, value) {
    document.documentElement.style.setProperty(name, value);
}

function getRootVar(name) {
    return document.documentElement.style.getPropertyValue(name);
}

function setColors(colors){
    setRootVar('--page-bg-color', colors["page_bg"]);
    setRootVar('--header-color', colors["header"]);
    setRootVar('--text-color', colors["text"]);
    setRootVar('--bg-color', colors["bg"]);
    setRootVar('--link-color', colors["link"]);
}

document.getElementById("theme_toggle").addEventListener("click", () => {
    if (theme === "light") {
        setColors(DARK_COLORS);
        theme = "dark";
    } else {
        setColors(LIGHT_COLORS);
        theme = "light";
    }
});



// ---------------------------------- навігація -----------------------------

document.addEventListener("keydown", (e) => {
    switch (e.key) {
        case "ArrowDown": go(1); break;
        case "ArrowUp": go(-1); break;
        case "PageDown": go(10); break;
        case "PageUp": go(-10); break;
        case "End": go(slides.length - 1); break;
    }
});

function go(delta) {
    current_slide_no += delta;
    
    var len = slides.length;
    if (current_slide_no < 0)
        current_slide_no = 0;
    else if (current_slide_no > len - 1)
        current_slide_no = len - 1;
    
    // Показати слайди з 0 по current_slide_no включно
    for (let i = 0; i < len; i++) {
        slides[i].style.display = i <= current_slide_no ? 'block' : "none";
    }
    // Фокус на останньому з видимих
    for (let i = 0; i < current_slide_no; i++) {
        slides[i].classList.remove('foc');
    }
    slides[current_slide_no].classList.add('foc');

    // Скролінг до дна останнього слайду с затримкою для рендерінгу браузера
    setTimeout(() => {
        const rect = slides[current_slide_no].getBoundingClientRect();
        const bottom = rect.bottom + window.scrollY;

        window.scrollTo({
            top: bottom - window.innerHeight + 100,
            behavior: "smooth"
        });
    }, 10);  

 }

// ------------------------- Малювання олівцем --------------------------------

let canvas = null;

document.getElementById("pensil").addEventListener("click", canvasPainter);

function canvasPainter() {
    if (canvas) {
        document.body.removeChild(canvas);
        canvas = null;
        return;
    }
    const n = current_slide_no;
    let pen_color = "red";

    canvas = document.createElement('canvas');
    canvas.width = slides[n].clientWidth;
    canvas.height = Math.max(slides[n].clientHeight, 200);
    canvas.style.zIndex = 1;
    canvas.style.position = 'absolute';

    canvas.style.top = slides[n].offsetTop + "px";
    canvas.style.left = slides[n].offsetLeft + "px";
    canvas.style.borderRight = `solid 1px ${pen_color}`;

    canvas.style.cursor = "url('sys/pic/pensil.png'), crosshair";

    canvas.setAttribute("tabindex", "0");

    document.body.appendChild(canvas);

    const ctx = canvas.getContext("2d");
    ctx.strokeStyle = pen_color;
    ctx.globalAlpha = 1; //0.05;
    ctx.lineWidth = 2;
    ctx.lineCap = "round";

    let curves = [], drawing = false; 

    canvas.onmousedown = function (e) {
        let x = e.pageX - e.target.offsetLeft,
            y = e.pageY - e.target.offsetTop;
        curves.push([{ "x": x, "y": y }]);
        drawing = true;
    };

    canvas.onmousemove = function (e) {
        if (drawing) {
            let x = e.pageX - e.target.offsetLeft, 
            y = e.pageY - e.target.offsetTop;
            let curve = curves[curves.length - 1]
            let last = curve[curve.length - 1];

            ctx.beginPath();
            ctx.moveTo(last.x, last.y);
            ctx.lineTo(x, y);
            ctx.stroke();
            curve.push({ "x": x, "y": y });
        }        
    };

    canvas.onmouseup = function (e) {
        if (drawing) {
            let curve = curves[curves.length - 1]
            transform(curve);
            drawing = false;
            draw();
        }
    };

    function transform(curve) {
        let first = curve[0], last = curve[curve.length - 1];
        let len = Math.hypot(first.x - last.x, first.y - last.y)
        if (len < 5) {
            // замкнена крива перетворюється у прямокутник
            rectangle(curve);
        } else if (is_straight_line(curve)) {
            // крива перетворюється у відрізок прямої
            curve.splice(1, curve.length - 2);
            // ver
            if (Math.abs(first.x - last.x) / len < 0.03) 
                first.x = last.x;
            // hor
            if (Math.abs(first.y - last.y) / len < 0.03) 
                first.y = last.y;
        } else {
            smooth(curve);
        }
    }

    function is_straight_line(curve) {
        let first = curve[0], last = curve[curve.length - 1];
        let lenX = last.x - first.x, lenY = last.y - first.y;
        
        let sum = 0;
        for (const p of curve) {
            let d = Math.abs(lenX * (first.y - p.y) - lenY * (first.x - p.x))
            sum += d;
        }
        let len = Math.hypot(first.x - last.x, first.y - last.y);
        let avg_distance = sum / (curve.length - 2) / len;
        return avg_distance < 4;
    }


    function rectangle(curve) { 
        let xs = curve.map(p => p.x);
        let ys = curve.map(p => p.y);
        let maxX = Math.max(...xs), minX = Math.min(...xs);
        let maxY = Math.max(...ys), minY = Math.min(...ys);
        curve.length = 0;
        curve.push({"x":minX, "y":minY}, {"x":minX, "y":maxY}, 
                {"x":maxX, "y":maxY}, {"x":maxX, "y":minY}, {"x":minX, "y":minY});
    }
        
    function smooth(curve) {   
        for (let k = 1; k < 2; k++) {
            for (let i = 1; i < curve.length - 1; i++) {
                curve[i].x = (curve[i-1].x + curve[i+1].x) / 2;
                curve[i].y = (curve[i-1].y + curve[i+1].y) / 2;     
            }
        } 
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let points of curves) {
            if (points.length < 2) 
                continue;
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.stroke();
        }
    }

    // Ctrl+Z видаляє останню криву
    canvas.onkeydown = function (e) {
        if (e.ctrlKey && e.key === "z") { 
            if (curves.length > 0) {
                curves.pop();
                draw();
            }
            e.preventDefault(); 
        }
    };

}

