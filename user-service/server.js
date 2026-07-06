// user-service/server.js
const express = require('express');
const app = express();

app.get('/users', (req, res) => {
  res.json([
    { id: 1, name: 'Alice', email: 'alice@example.com' },
    { id: 2, name: 'Bob',   email: 'bob@example.com'   },
  ]);
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

// app.listen(3000, () => console.log('User service on :3000'));

// server.js — add these lines at the very bottom

if (require.main === module) {
  // Only start the server if run directly (not during tests)
  app.listen(3000, () => console.log('User service on :3000'));
}

module.exports = app; // Export app so tests can import it