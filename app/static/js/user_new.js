
const namesArea = document.getElementById("namesArea");

document.getElementById("mailButton").addEventListener("click", (e) => {
  e.preventDefault();
  let addresses = namesArea.value.split("\n");
  let logins = [];
  for (let a of addresses) {
      a = a.trim();
      if (!a) continue;
      let i = a.indexOf("@");
      if (i == -1) {
         logins.push("ERROR: " + a)
      } else {
         let login = groupLetter.value + a[0].toUpperCase() + a.slice(1, i);
         logins.push(login)
      }
  }
  let loginsStr = logins.join("\n");
  // namesArea.value = loginsStr;
  replaceString(namesArea, loginsStr, 0, namesArea.value.length) 
});

