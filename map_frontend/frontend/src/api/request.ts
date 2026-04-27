import axios from 'axios';

/**
 * 规范化 API 根路径：后端路由挂载在 `/api` 下。
 * 若 .env 写成 `http://localhost:8000`（漏了 `/api`），会自动补为 `http://localhost:8000/api`。
 */
function normalizeApiBase(raw: string | undefined): string {
  const v = (raw ?? '/api').trim();
  if (!v || v === '/') return '/api';
  const noTrail = v.replace(/\/+$/, '');
  if (noTrail.endsWith('/api')) return noTrail;
  if (/^https?:\/\//i.test(noTrail)) {
    return `${noTrail}/api`;
  }
  return noTrail.startsWith('/') ? noTrail : `/${noTrail}`;
}

const resolvedBaseURL = normalizeApiBase(import.meta.env.VITE_API_BASE_URL);

/**
 * 联调用固定 JWT（`sub=1`，与 backend `create_access_token(1)` 一致、对应当前 .env 的 SECRET_KEY）。
 * 注意：纯字符串如 `my-test-token` 不是合法 JWT，后端会 401。
 * 若你修改了后端的 `SECRET_KEY`，请重新生成并替换本常量，或设 `localStorage.map_access_token`。
 */
const HARDCODED_DEV_BEARER =
  'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc5NDYxMTQzfQ.2ObLIjXzAe70Cr4bbOaRYojGdDwwzwcZkuwzQajrToE';

function resolveAuthorizationHeader(): string {
  if (typeof localStorage === 'undefined') {
    return HARDCODED_DEV_BEARER;
  }
  const raw = localStorage.getItem('map_access_token');
  if (!raw?.trim()) {
    return HARDCODED_DEV_BEARER;
  }
  const t = raw.trim();
  return /^Bearer\s+/i.test(t) ? t : `Bearer ${t}`;
}

export const http = axios.create({
  baseURL: resolvedBaseURL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

http.interceptors.request.use((config) => {
  config.headers.Authorization = resolveAuthorizationHeader();
  const path = `${config.baseURL ?? ''}${config.url ?? ''}`;
  if (path.includes('portal-snapshot') || path.includes('committee')) {
    // eslint-disable-next-line no-console
    console.log(
      '%c🌐 [MAP Axios 即将请求]',
      'color:#A78BFA;font-weight:bold',
      String(config.method ?? 'GET').toUpperCase(),
      path,
      { params: config.params },
    );
  }
  return config;
});

http.interceptors.response.use(
  (res) => {
    const path = `${res.config.baseURL ?? ''}${res.config.url ?? ''}`;
    if (path.includes('portal-snapshot') || path.includes('committee')) {
      // eslint-disable-next-line no-console
      console.log(
        '%c🌐 [MAP Axios 响应]',
        'color:#34C759;font-weight:bold',
        res.status,
        path,
      );
    }
    return res;
  },
  (err) => {
    if (axios.isAxiosError(err) && err.config) {
      const path = `${err.config.baseURL ?? ''}${err.config.url ?? ''}`;
      if (path.includes('portal-snapshot') || path.includes('committee')) {
        // eslint-disable-next-line no-console
        console.error(
          '%c🌐 [MAP Axios 错误]',
          'color:#F97316;font-weight:bold',
          err.response?.status,
          path,
          err.message,
        );
      }
    }
    return Promise.reject(err);
  },
);

export default http;
