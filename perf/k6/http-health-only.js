import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
	vus: __ENV.VUS ? parseInt(__ENV.VUS, 10) : 1,
	duration: __ENV.DURATION || '10s',
	thresholds: {
		http_req_failed: ['rate<0.01'],
	},
};

function baseUrl() {
	const raw = (__ENV.BASE_URL || 'http://[::1]').trim();
	// Keep consistent with the main perf scripts: normalize localhost -> IPv6 loopback.
	if (raw === 'http://localhost') return 'http://[::1]';
	if (raw === 'http://localhost/') return 'http://[::1]';
	return raw.replace(/\/$/, '');
}

export default function () {
	const url = `${baseUrl()}/api/v1/health/`;
	const res = http.get(url, { redirects: 0, timeout: '10s' });
	check(res, {
		'health is 200': (r) => r.status === 200,
	});
	sleep(0.2);
}

