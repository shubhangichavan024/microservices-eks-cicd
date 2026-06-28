// user-service/server.test.js
// Run with: npm test
// Uses Jest + Supertest to call your Express app without starting a real server

const request = require('supertest');
const app     = require('./server');   // Import app (not started, just exported)

describe('User Service API', () => {

  // ── Test: GET /users ──────────────────────────────────────────────────────
  test('GET /users → returns 200 with an array of users', async () => {
    const res = await request(app).get('/users');

    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body.length).toBeGreaterThan(0);
  });

  test('GET /users → each user has id, name, and email fields', async () => {
    const res = await request(app).get('/users');
    const user = res.body[0];

    expect(user).toHaveProperty('id');
    expect(user).toHaveProperty('name');
    expect(user).toHaveProperty('email');
  });

  // ── Test: GET /health ─────────────────────────────────────────────────────
  test('GET /health → returns { status: "ok" }', async () => {
    const res = await request(app).get('/health');

    expect(res.statusCode).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });

  // ── Test: 404 for unknown routes ─────────────────────────────────────────
  test('GET /unknown → returns 404', async () => {
    const res = await request(app).get('/unknown-route');
    expect(res.statusCode).toBe(404);
  });

});
