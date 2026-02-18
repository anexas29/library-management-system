const API = "http://127.0.0.1:8000";

function headers() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + localStorage.getItem("token"),
  };
}

async function addBook() {
  const mediaType = document.querySelector('input[name="media_type"]:checked')?.value || "book";
  const title = document.getElementById("title").value.trim();
  const author = document.getElementById("author").value.trim();
  const serialNo = document.getElementById("serial_no").value.trim();
  const category = document.getElementById("category").value.trim() || "general";
  const msg = document.getElementById("msg");

  if (!title || !author || !serialNo) {
    msg.innerText = "All fields are mandatory.";
    return;
  }

  const res = await fetch(`${API}/maintenance/add-book`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      media_type: mediaType,
      title,
      author,
      serial_no: serialNo,
      category,
    }),
  });
  const data = await res.json();
  msg.innerText = res.ok ? data.message : data.detail || "Add book failed";
}

async function addMembership() {
  const name = document.getElementById("name").value.trim();
  const duration = Number(document.querySelector('input[name="type"]:checked')?.value || "6");
  const msg = document.getElementById("msg");

  if (!name) {
    msg.innerText = "All fields are mandatory.";
    return;
  }

  const res = await fetch(`${API}/maintenance/add-membership`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      member_name: name,
      duration_months: duration,
    }),
  });
  const data = await res.json();
  msg.innerText = res.ok
    ? `Membership Created | Number: ${data.membership_number}`
    : data.detail || "Add membership failed";
}

async function updateMembership() {
  const number = document.getElementById("membership_number").value.trim();
  const action = document.querySelector('input[name="action"]:checked')?.value || "extend";
  const extension = Number(document.querySelector('input[name="extension"]:checked')?.value || "6");
  const msg = document.getElementById("msg");

  if (!number) {
    msg.innerText = "Membership number is mandatory.";
    return;
  }

  const res = await fetch(`${API}/maintenance/update-membership`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify({
      membership_number: number,
      action,
      extension_months: extension,
    }),
  });
  const data = await res.json();
  msg.innerText = res.ok ? data.message : data.detail || "Update membership failed";
}

async function loadMemberships() {
  const res = await fetch(`${API}/maintenance/memberships`, { headers: headers() });
  const data = await res.json();
  const ul = document.getElementById("members");
  ul.innerHTML = "";
  if (!res.ok) return;
  data.forEach((m) => {
    ul.innerHTML += `<li class="list-group-item">${m.name} - ${m.type} - ${m.membership_number}</li>`;
  });
}

async function manageUser() {
  const mode = document.querySelector('input[name="mode"]:checked')?.value || "new";
  const name = document.getElementById("name").value.trim();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const role = document.querySelector('input[name="role"]:checked')?.value || "user";
  const membershipNumber = document.getElementById("membership_number")?.value?.trim() || null;
  const msg = document.getElementById("msg");

  if (!name || !username) {
    msg.innerText = "Name and username are mandatory.";
    return;
  }
  if (mode === "new" && !password) {
    msg.innerText = "Password is mandatory for new user.";
    return;
  }

  const res = await fetch(`${API}/maintenance/user-management`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      mode,
      name,
      username,
      password: password || null,
      role,
      membership_number: membershipNumber,
    }),
  });
  const data = await res.json();
  msg.innerText = res.ok ? data.message : data.detail || "User management failed";
}
