// ---------------------- перетворює поштові адреси на логіни

const namesArea = document.getElementById("namesArea");

document.getElementById("mailButton").addEventListener("click", (e) => {
  e.preventDefault();
  let addresses = namesArea.value.split("\n");
  let logins = [];
  const re = /[a-zA-Z0-9]+\.([a-zA-Z0-9]+)@.*/;
  for (let addr of addresses) {
      addr = addr.trim();
      if (!addr) continue;
      const found = addr.match(re); 
      if (found) {
         let name = found[1];
         let login = groupLetter.value + name[0].toUpperCase() + name.slice(1);
         logins.push(login)
      } else {
         logins.push(`--------- Error in :  ${addr}`)
      }
  }
  let loginsStr = logins.join("\n");
  replaceString(namesArea, loginsStr, 0, namesArea.value.length) 
});

