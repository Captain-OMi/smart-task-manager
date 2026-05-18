// This file is used to connect the Smart Task Manager frontend with Flask REST APIs, handling user task CRUD actions, admin user/task loading, dashboard statistics, form reset behavior, and safe dynamic HTML rendering.

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}

function formatStatus(status) {
    return escapeHtml(String(status || "pending").replaceAll("_", " "));
}

function taskCard(task, adminMode = false) {
    const ownerInfo = adminMode
        ? `<p class="task-meta">Owner: ${escapeHtml(task.user_name)} (${escapeHtml(task.user_email)})</p>`
        : "";

    const actions = adminMode
        ? `<button class="danger small" data-admin-delete-task="${task.id}">Delete Task</button>`
        : `
            <button class="secondary small" data-edit-task="${task.id}">Edit</button>
            <button class="success-btn small" data-complete-task="${task.id}">Complete</button>
            <button class="danger small" data-delete-task="${task.id}">Delete</button>
        `;

    return `
        <article class="task-card" data-task='${escapeHtml(JSON.stringify(task))}'>
            <h3>${escapeHtml(task.title)}</h3>
            <span class="status ${escapeHtml(task.status)}">${formatStatus(task.status)}</span>
            <p class="muted">${escapeHtml(task.description || "No description added.")}</p>
            ${ownerInfo}
            <p class="task-meta">Created: ${escapeHtml(task.created_at || "-")}</p>
            <div class="task-actions">${actions}</div>
        </article>
    `;
}

async function loadTasks() {
    const taskList = document.querySelector("#taskList");
    if (!taskList) {
        return;
    }

    try {
        const data = await apiRequest("/tasks");
        const tasks = data.tasks || [];
        taskList.innerHTML = tasks.length
            ? tasks.map((task) => taskCard(task)).join("")
            : `<p class="muted">No tasks yet. Add your first task from the form.</p>`;

        document.querySelector("#totalTasks").textContent = tasks.length;
        document.querySelector("#completedTasks").textContent = tasks.filter((task) => task.status === "completed").length;
        document.querySelector("#pendingTasks").textContent = tasks.filter((task) => task.status !== "completed").length;
    } catch (error) {
        taskList.innerHTML = `<p class="flash error">${escapeHtml(error.message)}</p>`;
    }
}

function resetTaskForm() {
    const form = document.querySelector("#taskForm");
    if (!form) {
        return;
    }

    form.reset();
    document.querySelector("#taskId").value = "";
    document.querySelector("#formTitle").textContent = "Add Task";
}

async function saveTask(event) {
    event.preventDefault();

    const taskId = document.querySelector("#taskId").value;
    const payload = {
        id: taskId,
        title: document.querySelector("#taskTitle").value,
        description: document.querySelector("#taskDescription").value,
        status: document.querySelector("#taskStatus").value,
    };

    const url = taskId ? "/task/update" : "/task/add";
    const method = taskId ? "PUT" : "POST";

    await apiRequest(url, {
        method,
        body: JSON.stringify(payload),
    });

    resetTaskForm();
    await loadTasks();
}

async function handleTaskActions(event) {
    const editButton = event.target.closest("[data-edit-task]");
    const completeButton = event.target.closest("[data-complete-task]");
    const deleteButton = event.target.closest("[data-delete-task]");

    if (editButton) {
        const card = editButton.closest(".task-card");
        const task = JSON.parse(card.dataset.task);
        document.querySelector("#taskId").value = task.id;
        document.querySelector("#taskTitle").value = task.title;
        document.querySelector("#taskDescription").value = task.description || "";
        document.querySelector("#taskStatus").value = task.status;
        document.querySelector("#formTitle").textContent = "Update Task";
    }

    if (completeButton) {
        await apiRequest("/task/complete", {
            method: "PUT",
            body: JSON.stringify({ id: completeButton.dataset.completeTask }),
        });
        await loadTasks();
    }

    if (deleteButton && confirm("Delete this task?")) {
        await apiRequest("/task/delete", {
            method: "DELETE",
            body: JSON.stringify({ id: deleteButton.dataset.deleteTask }),
        });
        await loadTasks();
    }
}

async function loadUsers() {
    const userTable = document.querySelector("#userTable");
    if (!userTable) {
        return;
    }

    const data = await apiRequest("/users");
    const users = data.users || [];
    userTable.innerHTML = users.map((user) => `
        <tr>
            <td>${escapeHtml(user.name)}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>${escapeHtml(user.role)}</td>
            <td><button class="danger small" data-delete-user="${user.id}">Delete</button></td>
        </tr>
    `).join("");
    document.querySelector("#adminUserCount").textContent = users.length;
}

async function loadAdminTasks() {
    const adminTaskList = document.querySelector("#adminTaskList");
    if (!adminTaskList) {
        return;
    }

    const data = await apiRequest("/admin/tasks");
    const tasks = data.tasks || [];
    adminTaskList.innerHTML = tasks.length
        ? tasks.map((task) => taskCard(task, true)).join("")
        : `<p class="muted">No tasks available.</p>`;
    document.querySelector("#adminTaskCount").textContent = tasks.length;
}

async function handleAdminActions(event) {
    const deleteUserButton = event.target.closest("[data-delete-user]");
    const deleteTaskButton = event.target.closest("[data-admin-delete-task]");

    if (deleteUserButton && confirm("Delete this user and their tasks?")) {
        await apiRequest("/user/delete", {
            method: "DELETE",
            body: JSON.stringify({ id: deleteUserButton.dataset.deleteUser }),
        });
        await loadUsers();
        await loadAdminTasks();
    }

    if (deleteTaskButton && confirm("Delete this task?")) {
        await apiRequest("/admin/task/delete", {
            method: "DELETE",
            body: JSON.stringify({ id: deleteTaskButton.dataset.adminDeleteTask }),
        });
        await loadAdminTasks();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const taskForm = document.querySelector("#taskForm");
    const taskList = document.querySelector("#taskList");
    const resetButton = document.querySelector("#resetTaskForm");
    const refreshTasks = document.querySelector("#refreshTasks");
    const refreshUsers = document.querySelector("#refreshUsers");
    const refreshAdminTasks = document.querySelector("#refreshAdminTasks");
    const adminUserTable = document.querySelector("#userTable");
    const adminTaskList = document.querySelector("#adminTaskList");

    if (taskForm) {
        taskForm.addEventListener("submit", saveTask);
        resetButton.addEventListener("click", resetTaskForm);
        refreshTasks.addEventListener("click", loadTasks);
        taskList.addEventListener("click", handleTaskActions);
        loadTasks();
    }

    if (adminUserTable || adminTaskList) {
        refreshUsers.addEventListener("click", loadUsers);
        refreshAdminTasks.addEventListener("click", loadAdminTasks);
        document.body.addEventListener("click", handleAdminActions);
        loadUsers();
        loadAdminTasks();
    }
});
