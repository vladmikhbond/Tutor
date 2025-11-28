// -----------------------перемикач тем --------------------------

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