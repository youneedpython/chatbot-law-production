// frontend/src/api/client.js
// Centralized API client for chatbot-law-prod


// export async function apiFetch(path, options = {}) {
    //     return fetch(`/api${path}`, {
        //         headers: {"Content-Type": "application/json", ...(options.headers || {}) },
        //         ...options,
        //     });
// }
        
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

console.log('API_BASE_URL >> ', API_BASE_URL);

export async function apiFetch(path, options = {}) {
    return fetch(`${API_BASE_URL}${path}`, {
        headers: {"Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    });
}