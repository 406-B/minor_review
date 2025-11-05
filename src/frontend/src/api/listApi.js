import request from './request';

export function login(data) {
	// PATCH/POST 以实际后端为准
	return request.patch('/api/v1/login', data);
}

export function register(data) {
	return request.post('/api/v1/register', data);
}

// 其它原有API...
