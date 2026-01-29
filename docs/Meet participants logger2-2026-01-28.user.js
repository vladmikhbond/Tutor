// ==UserScript==
// @name          Meet participants logger2
// @namespace    http://tampermonkey.net/
// @version      2026-01-28
// @description  try to take over the world!
// @author       You
// @match        https://meet.google.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @grant        none
// ==/UserScript==

const INTERVAL = 10_000;
const URL = "http://127.0.0.1:7003/attend/snapshot";
const USERNAME = "tutor";

function getParticipants() 
{
  const items = document.querySelectorAll('[role="listitem"]');
  return [...items]
    .map(item => {
      // найчастіше тут "Ім'я Прізвище"
      return item.getAttribute("aria-label");
    })
    .filter(name =>
      name &&
      !name.toLowerCase().includes("you") &&
      !name.toLowerCase().includes("ви")
    );
}

setInterval(() => {
  const data = {
    username: USERNAME,
    visitors: getParticipants()
  };
  // console.log("MEET SNAPSHOT", data);
  fetch(URL, {
     method: "POST",
     headers: {
         "Content-Type": "application/json",
         "X-API-Key": "secret123"
     },
     body: JSON.stringify(data)
  })
  .then(r => {
     console.log("STATUS", r.status);
     return r.text();
  })
  .then(t => console.log("BODY", t))
  .catch(console.error);
}, INTERVAL);
