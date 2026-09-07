const apiBase = window.KISHAN_CONFIG?.API_BASE_URL || "http://localhost:8000/api/v1";
window.KishanAPI = {
  token: () => localStorage.getItem("kishan_token"),
  async request(path, options = {}) {
    const headers = {"Content-Type":"application/json", ...(options.headers || {})};
    if (this.token()) headers.Authorization = `Bearer ${this.token()}`;
    const response = await fetch(`${apiBase}${path}`, {...options, headers});
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "অনুরোধটি সম্পন্ন হয়নি");
    return data;
  },
  async register(payload) { const data = await this.request("/auth/register", {method:"POST", body:JSON.stringify(payload)}); localStorage.setItem("kishan_token", data.access_token); return data; },
  async login(payload) { const data = await this.request("/auth/login", {method:"POST", body:JSON.stringify(payload)}); localStorage.setItem("kishan_token", data.access_token); return data; },
  fields: () => window.KishanAPI.request("/fields"),
  createField: payload => window.KishanAPI.request("/fields", {method:"POST", body:JSON.stringify(payload)}),
  createTest: payload => window.KishanAPI.request("/soil-tests", {method:"POST", body:JSON.stringify(payload)}),
  analyze: id => window.KishanAPI.request(`/soil-tests/${id}/analyze`, {method:"POST"})
};
