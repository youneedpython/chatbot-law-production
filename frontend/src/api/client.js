// frontend/src/api/client.js
// Centralized API client for chatbot-law-prod


export async function apiFetch(path, options = {}) {
    const res = await fetch(`/api${path}`, {
        headers: { "Content-Type": "application/json", ...(options.headers || {})},
        ...options,
    });

    // Fast fail with readable error
    if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
    }

    // Most endpoints return JSON
    const ct = res.headers.get("content-type") || "";
    return ct.includes("application/json") ? res.json() : res.text();    
}