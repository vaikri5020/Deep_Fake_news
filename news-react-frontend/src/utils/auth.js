// Simple localStorage-based auth (swap for real API calls when ready)

const USER_KEY  = 'nv_user';
const USERS_KEY = 'nv_users';

export const Auth = {
  get() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)) || null; }
    catch { return null; }
  },
  set(user) { localStorage.setItem(USER_KEY, JSON.stringify(user)); },
  clear()   { localStorage.removeItem(USER_KEY); },
  isLoggedIn() { return !!this.get(); },
};

export function getStoredUsers() {
  try { return JSON.parse(localStorage.getItem(USERS_KEY)) || []; }
  catch { return []; }
}

export function saveUser(user) {
  const users = getStoredUsers();
  users.push(user);
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function findUser(email, password) {
  return getStoredUsers().find(u => u.email === email && u.password === password) || null;
}
