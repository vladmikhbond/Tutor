// те саме, що в роутері
const USER_FILTER_KEY = "TUTOR_user_filter"
const inp = document.getElementById("user_filter");

inp.value = getCookie(USER_FILTER_KEY);

inp.addEventListener("change", async (e) => {
   setCookie(USER_FILTER_KEY, encodeURIComponent(inp.value.trim()));
   location.reload();
})

// Встановлення або видалення кукі
function setCookie(key, value) {
   if (value) {
      const maxAge = 60 * 60 * 24 * 365; // seconds
      document.cookie = `${key}=${value}; max-age=${maxAge}; path=/; SameSite=Lax;`;
   } else {
      document.cookie = `${key}=; max-age=0; path=/`;
   }
}

// Отримання кукі
function getCookie(key) {
   const pairs = document.cookie.split('; ').map(v => v.split('='));
   const pair = pairs.find(([k]) => k === key);
   return pair ? decodeURIComponent(pair[1]) : "";
}   
