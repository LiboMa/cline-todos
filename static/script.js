document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const authSection = document.getElementById('auth-section');
    const todoSection = document.getElementById('todo-section');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const todoForm = document.getElementById('todo-form');
    const todoInput = document.getElementById('todo-input');
    const commentInput = document.getElementById('comment-input');
    const todoList = document.getElementById('todo-list');
    const logoutBtn = document.getElementById('logout-btn');
    const usernameDisplay = document.getElementById('username-display');
    const authTabs = document.querySelectorAll('.auth-tab');

    const API_URL = '/api';
    let accessToken = localStorage.getItem('accessToken');
    let currentUser = localStorage.getItem('currentUser') ? JSON.parse(localStorage.getItem('currentUser')) : null;

    // Debug logging
    console.log('Initial state:', { accessToken, currentUser });

    // Auth Tab Switching
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const formId = tab.dataset.form;
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.auth-form').forEach(form => {
                form.classList.add('hidden');
            });
            document.getElementById(formId).classList.remove('hidden');
        });
    });

    // Check Authentication Status
    function checkAuth() {
        console.log('Checking auth status:', { accessToken, currentUser });
        if (accessToken && currentUser) {
            authSection.classList.add('hidden');
            todoSection.classList.remove('hidden');
            usernameDisplay.textContent = `Welcome, ${currentUser.username}!`;
            fetchTodos();
        } else {
            authSection.classList.remove('hidden');
            todoSection.classList.add('hidden');
            todoList.innerHTML = '';
        }
    }

    // API Helpers
    async function apiRequest(endpoint, options = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...(accessToken && { 'Authorization': `Bearer ${accessToken}` })
            };

            console.log('Making API request:', {
                url: `${API_URL}${endpoint}`,
                method: options.method || 'GET',
                headers,
                body: options.body
            });

            const response = await fetch(`${API_URL}${endpoint}`, {
                ...options,
                headers
            });

            console.log('API response status:', response.status);

            // Handle 204 No Content response (successful deletion)
            if (response.status === 204) {
                return null;
            }

            const data = await response.json();
            console.log('API response data:', data);

            if (response.status === 401) {
                logout();
                throw new Error(data.error || 'Session expired. Please login again.');
            }

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Something went wrong');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth Functions
    async function login(username, password) {
        try {
            console.log('Attempting login for:', username);
            const data = await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            console.log('Login successful:', data);
            accessToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            checkAuth();
        } catch (error) {
            console.error('Login error:', error);
            alert(error.message);
        }
    }

    async function register(username, email, password) {
        try {
            console.log('Attempting registration for:', username);
            const data = await apiRequest('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
            
            console.log('Registration successful:', data);
            accessToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            checkAuth();
        } catch (error) {
            console.error('Registration error:', error);
            alert(error.message);
        }
    }

    function logout() {
        console.log('Logging out');
        accessToken = null;
        currentUser = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('currentUser');
        checkAuth();
    }

    // Todo Functions
    async function fetchTodos() {
        try {
            const todos = await apiRequest('/todos');
            console.log('Fetched todos:', todos);
            renderTodos(todos);
        } catch (error) {
            console.error('Error fetching todos:', error);
            alert(error.message);
        }
    }

    function formatDate(isoString) {
        try {
            const date = new Date(isoString);
            if (isNaN(date.getTime())) {
                return 'Invalid date';
            }
            return date.toLocaleString();
        } catch (error) {
            console.error('Error formatting date:', error);
            return 'Invalid date';
        }
    }

    function renderTodos(todos) {
        todoList.innerHTML = '';
        if (!Array.isArray(todos)) {
            console.error('Expected todos to be an array, got:', todos);
            return;
        }
        
        todos.forEach((todo) => {
            const li = document.createElement('li');
            li.className = 'todo-item';
            
            li.innerHTML = `
                <div class="todo-content">
                    <h3 class="todo-name">${todo.name || ''}</h3>
                    <p class="todo-comment">${todo.comment || ''}</p>
                    <small class="todo-timestamp">Created: ${formatDate(todo.timestamp)}</small>
                </div>
                <div class="todo-actions">
                    <button class="edit-btn">Edit</button>
                    <button class="delete-btn">Delete</button>
                </div>
            `;

            // Edit todo
            const editBtn = li.querySelector('.edit-btn');
            editBtn.addEventListener('click', async () => {
                const newName = prompt('Edit todo name:', todo.name);
                if (newName === null) return; // User cancelled
                
                const newComment = prompt('Edit comment:', todo.comment || '');
                if (newComment === null) return; // User cancelled
                
                if (newName.trim()) {  // Ensure name is not empty
                    await updateTodo(todo.id, {
                        name: newName.trim(),
                        comment: newComment.trim()
                    });
                } else {
                    alert('Todo name cannot be empty');
                }
            });

            // Delete todo
            const deleteBtn = li.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this todo?')) {
                    await deleteTodo(todo.id);
                }
            });

            todoList.appendChild(li);
        });
    }

    async function addTodo(name, comment) {
        try {
            await apiRequest('/todos', {
                method: 'POST',
                body: JSON.stringify({ name, comment })
            });
            fetchTodos();
        } catch (error) {
            console.error('Error adding todo:', error);
            alert(error.message);
        }
    }

    async function updateTodo(id, data) {
        try {
            await apiRequest(`/todos/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            fetchTodos();
        } catch (error) {
            console.error('Error updating todo:', error);
            alert(error.message);
        }
    }

    async function deleteTodo(id) {
        try {
            await apiRequest(`/todos/${id}`, {
                method: 'DELETE'
            });
            fetchTodos();
        } catch (error) {
            console.error('Error deleting todo:', error);
            alert(error.message);
        }
    }

    // Event Listeners
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        if (!username || !password) {
            alert('Please fill in all fields');
            return;
        }
        login(username, password);
    });

    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        if (!username || !email || !password) {
            alert('Please fill in all fields');
            return;
        }
        register(username, email, password);
    });

    todoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = todoInput.value.trim();
        const comment = commentInput.value.trim();
        
        if (name) {
            addTodo(name, comment);
            todoInput.value = '';
            commentInput.value = '';
        } else {
            alert('Todo name cannot be empty');
        }
    });

    logoutBtn.addEventListener('click', logout);

    // Initial auth check
    checkAuth();
});
