import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("qs_access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry && !original.url.includes("/auth/login")) {
      original._retry = true;
      const refresh = localStorage.getItem("qs_refresh");
      if (refresh) {
        try {
          const { data } = await axios.post("/api/auth/refresh/", { refresh });
          localStorage.setItem("qs_access", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem("qs_access");
          localStorage.removeItem("qs_refresh");
        }
      }
    }
    return Promise.reject(error);
  }
);

export function errorMessage(err) {
  if (err.response?.data?.message) return err.response.data.message;
  if (err.response?.data?.detail) return err.response.data.detail;
  const data = err.response?.data;
  if (data && typeof data === "object") {
    const firstError = Object.values(data).find((v) => typeof v === "string");
    if (firstError) return firstError;
    const firstList = Object.values(data).find((v) => Array.isArray(v) && v.length > 0);
    if (firstList) return Array.isArray(firstList[0]) ? firstList[0][0] : firstList[0];
  }
  if (err.response?.status === 500) return "Serverda xatolik yuz berdi. Keyinroq urinib ko'ring.";
  if (!err.response) return "Serverga ulanib bo'lmadi. Backend ishlayotganini tekshiring.";
  return "Xatolik yuz berdi.";
}

export default api;
