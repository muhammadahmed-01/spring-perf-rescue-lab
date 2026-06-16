import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const ENDPOINT = __ENV.ENDPOINT || '/api/orders/buggy';
const MODE = __ENV.MODE || 'buggy';

const DEFAULT_VUS = 100;
const DEFAULT_ITERATIONS = 100000;

export const options = {
  scenarios: {
    load: {
      executor: 'shared-iterations',
      vus: __ENV.VUS ? Number(__ENV.VUS) : DEFAULT_VUS,
      iterations: __ENV.ITERATIONS ? Number(__ENV.ITERATIONS) : DEFAULT_ITERATIONS,
      maxDuration: __ENV.MAX_DURATION || '15m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<10000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const response = http.get(`${BASE_URL}${ENDPOINT}`);
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has query count header': (r) => r.headers['X-Query-Count'] !== undefined,
  });
}

export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const p99 = data.metrics.http_req_duration.values['p(99)'];
  const avg = data.metrics.http_req_duration.values.avg;
  const rps = data.metrics.http_reqs.values.rate;
  const totalRequests = data.metrics.http_reqs.values.count;
  const failedRate = data.metrics.http_req_failed
    ? data.metrics.http_req_failed.values.rate
    : 0;
  const vus = __ENV.VUS ? Number(__ENV.VUS) : DEFAULT_VUS;
  const iterations = __ENV.ITERATIONS ? Number(__ENV.ITERATIONS) : DEFAULT_ITERATIONS;

  const summary = {
    mode: MODE,
    endpoint: ENDPOINT,
    vus,
    iterations,
    total_requests: totalRequests,
    p95_ms: Math.round(p95),
    p99_ms: Math.round(p99),
    avg_ms: Math.round(avg),
    rps: Number(rps.toFixed(2)),
    error_rate_pct: Number((failedRate * 100).toFixed(2)),
    timestamp: new Date().toISOString(),
  };

  return {
    stdout: JSON.stringify(summary, null, 2) + '\n',
    [`load/results/${MODE}-summary.json`]: JSON.stringify(summary, null, 2),
  };
}
