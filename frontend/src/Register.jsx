import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

function Register({ setAuth, setUsername }) {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: ''
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await axios.post(`${API_URL}/register`, form, {
        withCredentials: true,
      });
      
      setMessage(res.data.message);

      // Auto-login after successful registration
      if (res.status === 201) {
        setAuth(true);
        setUsername(res.data.username);
      }
    } catch (err) {
      if (err.response && err.response.data) {
        setMessage(err.response.data.message || "Registration failed.");
      } else {
        setMessage("Server error. Try again.");
      }
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      {message && <p style={{ color: message.includes('successfully') ? 'green' : 'red' }}>{message}</p>}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          placeholder="Enter username"
          value={form.username}
          onChange={handleChange}
          required
        />
        <br />
        <input
          type="email"
          name="email"
          placeholder="Enter email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <br />
        <input
          type="password"
          name="password"
          placeholder="Enter password"
          value={form.password}
          onChange={handleChange}
          required
        />
        <br />
        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default Register;
