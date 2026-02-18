const API = "http://127.0.0.1:8000";

function reportHeaders() {
  return { Authorization: "Bearer " + localStorage.getItem("token") };
}

function setDashboardLink() {
  const role = localStorage.getItem("role");
  const link = document.querySelector(".nav-links a");
  if (!link) return;
  link.href = role === "admin" ? "../admin_home.html" : "../user_home.html";
}

async function loadIssuedReport() {
  const msg = document.getElementById("msg");
  if (msg) msg.innerText = "";
  const res = await fetch(`${API}/reports/issued-books`, { headers: reportHeaders() });
  const data = await res.json();
  const table = document.getElementById("table");
  table.innerHTML = "<tr><th>Transaction</th><th>User</th><th>Book</th><th>Issue</th><th>Due</th><th>Status</th></tr>";
  if (!res.ok) {
    if (msg) msg.innerText = data.detail || "Unable to load issued books report";
    return;
  }
  data.forEach((r) => {
    table.innerHTML += `<tr><td>${r.transaction_id}</td><td>${r.user_id}</td><td>${r.book_id}</td><td>${r.issue_date}</td><td>${r.due_date}</td><td>${r.status}</td></tr>`;
  });
}

async function loadFineReports() {
  const msg = document.getElementById("msg");
  if (msg) msg.innerText = "";
  const res = await fetch(`${API}/reports/fine-report`, { headers: reportHeaders() });
  const data = await res.json();
  const table = document.getElementById("fineTable");
  table.innerHTML = `
    <tr>
      <th>Transaction ID</th><th>User ID</th><th>Book ID</th><th>Due Date</th>
      <th>Return Date</th><th>Fine</th><th>Paid</th><th>Status</th>
    </tr>`;
  if (!res.ok) {
    if (msg) msg.innerText = data.detail || "Unable to load fine report";
    return;
  }
  data.forEach((t) => {
    table.innerHTML += `<tr><td>${t.transaction_id}</td><td>${t.user_id}</td><td>${t.book_id}</td><td>${t.due_date}</td><td>${t.return_date ?? "-"}</td><td>${t.fine}</td><td>${t.fine_paid}</td><td>${t.status}</td></tr>`;
  });
}

window.addEventListener("DOMContentLoaded", setDashboardLink);
