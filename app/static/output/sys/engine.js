// ---------------------- Зовнішні параметри -----------------------
// START_SLIDE_NO={0}; 
// VERSION = "tutor";
// IMG_HEIGHT_FACTOR = {0.33}

// ----------------------- перемикач тем --------------------------

document.getElementById("theme_toggle").addEventListener("click", () => 
{
    const link = document.getElementById("theme_link");
    let theme = link.getAttribute("href").slice(4,-4);   // 'sys/{THEME}.css'

    if (theme.endsWith("dark")) {
        theme = theme.slice(0, -4) + "light";
    } else {
        theme = theme.slice(0, -5) + "dark";
    }
    link.setAttribute("href", `sys/${theme}.css`);   
});

// ------------------------------- init ------------------------------------------
let current_slide_no = START_SLIDE_NO; // номер сфокусованого слйду
let slides = document.querySelectorAll("#lecture > div");
go(0);

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

// ------------------------- Painting on the canvas --------------------------------

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
            smooth(curve);
            smooth(curve);
            drawing = false;
            draw();
        }
    };

    function smooth(curve) {
        for (let i = 1; i < curve.length - 1; i++) {
            curve[i].x = (curve[i-1].x + curve[i+1].x) / 2;
            curve[i].y = (curve[i-1].y + curve[i+1].y) / 2;     
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

    // Перевірка на Ctrl+Z
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

