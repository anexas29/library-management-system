const API = "http://127.0.0.1:8000";

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + localStorage.getItem("token"),
  };
}

function setDashboardLink() {
  const role = localStorage.getItem("role");
  const link = document.querySelector(".nav-links a");
  if (!link) return;
  link.href = role === "admin" ? "../admin_home.html" : "../user_home.html";
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function addDaysISO(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

async function searchAvailableBooks() {
  const title = document.getElementById("search_title")?.value?.trim();
  const mediaType = document.querySelector('input[name="media_type"]:checked')?.value;
  const msg = document.getElementById("msg");

  if (!title && !mediaType) {
    msg.innerText = "Enter book name or select type before search.";
    return;
  }

  const query = new URLSearchParams();
  if (title) query.append("title", title);
  if (mediaType) query.append("media_type", mediaType);

  const res = await fetch(`${API}/transactions/book-available?${query.toString()}`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  const table = document.getElementById("booksTable");
  table.innerHTML = `
    <tr>
      <th>Select</th>
      <th>Book</th>
      <th>Author</th>
      <th>Serial No</th>
      <th>Type</th>
    </tr>`;

  if (!res.ok) {
    msg.innerText = data.detail || "Unable to fetch books";
    return;
  }

  if (!data.length) {
    msg.innerText = "No books found.";
    return;
  }

  data.forEach((book) => {
    table.innerHTML += `
      <tr>
        <td><input type="radio" name="book" value="${book.id}" data-title="${book.title}" data-author="${book.author}"></td>
        <td>${book.title}</td>
        <td>${book.author}</td>
        <td>${book.serial_no}</td>
        <td>${book.media_type}</td>
      </tr>`;
  });

  document.querySelectorAll('input[name="book"]').forEach((r) => {
    r.addEventListener("change", (e) => {
      document.getElementById("book_name").value = e.target.dataset.title;
      document.getElementById("author_name").value = e.target.dataset.author;
    });
  });
  msg.innerText = "";
}

async function issueBook() {
  const selected = document.querySelector('input[name="book"]:checked');
  const userId = document.getElementById("user_id").value.trim();
  const issueDate = document.getElementById("issue_date").value;
  const returnDate = document.getElementById("return_date").value;
  const remarks = document.getElementById("remarks").value.trim();
  const msg = document.getElementById("msg");

  if (!selected || !userId || !issueDate || !returnDate) {
    msg.innerText = "Please complete all mandatory fields and select a book.";
    return;
  }

  const issue = new Date(issueDate);
  const ret = new Date(returnDate);
  const max = new Date(issueDate);
  max.setDate(max.getDate() + 15);

  if (issueDate < todayISO()) {
    msg.innerText = "Issue date cannot be lesser than today.";
    return;
  }
  if (ret > max || ret < issue) {
    msg.innerText = "Return date must be between issue date and 15 days ahead.";
    return;
  }

  const res = await fetch(`${API}/transactions/issue-book`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      user_id: Number(userId),
      book_id: Number(selected.value),
      issue_date: issueDate,
      return_date: returnDate,
      remarks: remarks || null,
    }),
  });
  const data = await res.json();
  msg.innerText = res.ok
    ? `Book issued successfully. Transaction ID: ${data.transaction_id}`
    : data.detail || "Issue failed";
}

async function returnBook() {
  const transactionId = document.getElementById("transaction_id").value.trim();
  const serialNo = document.getElementById("serial_no").value.trim();
  const returnDate = document.getElementById("actual_return_date").value;
  const msg = document.getElementById("msg");

  if (!transactionId || !serialNo || !returnDate) {
    msg.innerText = "Transaction ID, serial number and return date are mandatory.";
    return;
  }

  const res = await fetch(`${API}/transactions/return-book`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      transaction_id: Number(transactionId),
      serial_no: serialNo,
      return_date: returnDate,
    }),
  });
  const data = await res.json();
  if (!res.ok) {
    msg.innerText = data.detail || "Return validation failed";
    return;
  }
  localStorage.setItem("return_txn_id", String(data.transaction_id));
  localStorage.setItem("return_fine", String(data.fine));
  msg.innerText = `Validated. Proceed to Pay Fine page. Fine: ${data.fine}`;
}

async function payFine() {
  const txnId = localStorage.getItem("return_txn_id");
  const finePaid = document.getElementById("fine_paid").checked;
  const remarks = document.getElementById("fine_remarks").value.trim();
  const msg = document.getElementById("msg");

  if (!txnId) {
    msg.innerText = "No return transaction found. Use Return Book first.";
    return;
  }

  const res = await fetch(`${API}/transactions/pay-fine`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      transaction_id: Number(txnId),
      fine_paid: finePaid,
      remarks: remarks || null,
    }),
  });
  const data = await res.json();
  msg.innerText = res.ok ? data.message : data.detail || "Payment failed";
}

async function loadActiveIssues() {
  const msg = document.getElementById("msg");
  if (msg) msg.innerText = "";
  const res = await fetch(`${API}/transactions/active-issues`, { headers: authHeaders() });
  const data = await res.json();
  const list = document.getElementById("activeList");
  list.innerHTML = "";
  if (!res.ok) {
    if (msg) msg.innerText = data.detail || "Unable to load active issues";
    return;
  }
  if (!data.length) {
    if (msg) msg.innerText = "No active issues found.";
    return;
  }
  data.forEach((t) => {
    list.innerHTML += `<li class="list-group-item">Txn ${t.transaction_id} | User ${t.user_id} | Book ${t.book_id} | Due ${t.due_date}</li>`;
  });
}

async function loadOverdueReturns() {
  const msg = document.getElementById("msg");
  if (msg) msg.innerText = "";
  const res = await fetch(`${API}/transactions/overdue-returns`, { headers: authHeaders() });
  const data = await res.json();
  const table = document.getElementById("overdueTable");
  table.innerHTML = `
    <tr>
      <th>Transaction</th><th>User</th><th>Book</th><th>Due Date</th><th>Days Late</th><th>Fine</th>
    </tr>`;
  if (!res.ok) {
    if (msg) msg.innerText = data.detail || "Unable to load overdue returns";
    return;
  }
  if (!data.length) {
    if (msg) msg.innerText = "No overdue returns found.";
    return;
  }
  data.forEach((t) => {
    table.innerHTML += `<tr><td>${t.transaction_id}</td><td>${t.user_id}</td><td>${t.book_id}</td><td>${t.due_date}</td><td>${t.days_late}</td><td>${t.fine}</td></tr>`;
  });
}

window.addEventListener("DOMContentLoaded", () => {
  setDashboardLink();

  const issueDate = document.getElementById("issue_date");
  const returnDate = document.getElementById("return_date");
  if (issueDate && returnDate) {
    issueDate.value = todayISO();
    returnDate.value = addDaysISO(15);
    issueDate.addEventListener("change", () => {
      returnDate.value = addDaysISO(15);
    });
  }

  const actualReturnDate = document.getElementById("actual_return_date");
  if (actualReturnDate) {
    actualReturnDate.value = todayISO();
  }
});
