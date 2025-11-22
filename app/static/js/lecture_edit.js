// ----------------- confext menu ---------------------

const menu = document.getElementById("context-menu");
const content = document.getElementById("content");

// Показати меню
content.addEventListener("contextmenu", e => {
  e.preventDefault();
  menu.style.display = "block";
  menu.style.left = e.pageX + "px";
  menu.style.top = e.pageY + "px";
});

// Приховати меню при кліку
content.addEventListener("click", () => {
  menu.style.display = "none";
});

// --------------------- upload picture --------------------

const upload_form = document.getElementById("upload_form")

upload_form.addEventListener("submit", async function(e) 
{
  e.stopPropagation(); 
  e.preventDefault();  
  // Create a formdata object and add the files
  let data = new FormData();
  let files = document.getElementById('file').files;
  if (files && files.length) {
      data.append('file', files[0]);
  }

  const disc_id = document.getElementById("disc_id");  
  data.append('disc_id', disc_id.value);

  // POST to server
  fetch('/lecture/picture', {
    method: 'POST',
    body: data
  }).then(function(response) {
    if (!response.ok) throw new Error('Upload failed: ' + response.status);
    return response.json().catch(function(){ return null; });
  }).then(function(json) {
    // on success - reload or update UI (minimal handling)
    window.location.reload();
  }).catch(function(err) {
    alert('Upload error: ' + err.message);
  });
});
