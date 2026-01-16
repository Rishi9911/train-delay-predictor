import React, { useState } from 'react';
import axios from 'axios';

function Login({ setAuth, setUsername }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        'http://localhost:5000/login', 
        form, 
        { withCredentials: true } // important for Flask session
      );
      setAuth(true);
      setUsername(res.data.username);
      setError('');
    } catch (err) {
      setError('Invalid username or password');
      console.error('Login failed:', err.response?.data || err.message);
    }
  };

  return (
    <div>
      <h3>Login</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input name="username" placeholder="Username" onChange={handleChange} required />
        <input name="password" type="password" placeholder="Password" onChange={handleChange} required />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
