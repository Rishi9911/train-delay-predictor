import React, { useEffect, useState } from "react";
import axios from "axios";
import Login from "./Login";
import Register from "./Register";
import "./App.css";
import { API_URL } from "./config";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { motion, AnimatePresence } from "framer-motion";
import { FaHome, FaHistory, FaCog, FaTrain, FaUserCircle } from "react-icons/fa";
// import { MdEmail } from "react-icons/md";


axios.defaults.withCredentials = true;

function App() {
  const [auth, setAuth] = useState(false);
  const [username, setUsername] = useState("");
  const [showPredictForm, setShowPredictForm] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [form, setForm] = useState({
    date: "",
    temperature: "",
    rain: 0,
    fog: 0,
    visibility: "",
    windspeed: "",
  });
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    document.body.className = darkMode ? "dark-mode" : "";
  }, [darkMode]);

  // Fetch username on refresh
  useEffect(() => {
    axios.get(`${API_URL}/profile`, { withCredentials: true })
      .then(res => {
        if (res.data.username) {
          setAuth(true);
          setUsername(res.data.username);
        }
      })
      .catch(() => { });
  }, []);

  const handleLogout = async () => {
    await axios.post(`${API_URL}/logout`, {}, { withCredentials: true });
    setAuth(false);
    setUsername("");
    setResult(null);
    setHistory([]);
    setShowPredictForm(false);
    setShowHistory(false);
    toast.info("Logged out successfully!");
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/history`, { withCredentials: true });
      setHistory(res.data);
    } catch {
      toast.error("Failed to fetch history.");
    }
  };

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/predict`, form, { withCredentials: true });
      setResult(res.data.predicted_delay);
      toast.success(`Predicted Delay: ${res.data.predicted_delay} min`);
    } catch {
      toast.error("Prediction failed!");
    }
  };

  /** ------------------ Navbar ------------------ **/
  const Navbar = () => (
    <div className="navbar">
      <div className="nav-left"><FaTrain /> Train Delay Predictor</div>
      <div className="nav-right">
        <button onClick={() => {
          window.scrollTo({ top: 0, behavior: "smooth" });
          setShowPredictForm(false);
          setShowHistory(false);
        }}>
          <FaHome /> Home
        </button>

        {auth && (
          <button onClick={() => {
            setShowPredictForm(true);
            setShowHistory(false);
            setResult(null);
            setTimeout(() => document.getElementById("predict-section")?.scrollIntoView({ behavior: "smooth" }), 200);
          }}>
            Predict
          </button>
        )}

        {auth && (
          <button onClick={() => {
            fetchHistory();
            setShowHistory(true);
            setShowPredictForm(false);
            setTimeout(() => document.getElementById("history-section")?.scrollIntoView({ behavior: "smooth" }), 200);
          }}>
            <FaHistory /> History
          </button>
        )}

        <button onClick={() => setDarkMode(!darkMode)}>Theme</button>

        {auth ? (
          <>
            <span className="user-info"><FaUserCircle /> {username || "User"}</span>
            <button className="logout-btn" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <button className="login-btn" onClick={() => setShowModal(true)}>Login / Register</button>
        )}

        <button onClick={() => alert("Settings coming soon!")}><FaCog /></button>
      </div>
    </div>
  );

  /** ------------------ Login/Register Modal ------------------ **/
  const AuthModal = () => (
    <div className="modal-overlay">
      <motion.div
        className="modal-content auth-card"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Close Button */}
        <button className="close-btn" onClick={() => setShowModal(false)}>×</button>

        <h2>{showRegister ? "" : ""}</h2>
        {showRegister ? (
          <Register
            setAuth={(status) => {
              setAuth(status);
              if (status) handleLoginSuccess();
            }}
            setUsername={setUsername}
          />
        ) : (
          <Login
            setAuth={(status) => {
              setAuth(status);
              if (status) handleLoginSuccess();
            }}
            setUsername={setUsername}
          />
        )}
        <p onClick={() => setShowRegister(!showRegister)} className="switch-auth">
          {showRegister ? "Already have an account? Login" : "New user? Register"}
        </p>
      </motion.div>
    </div>
  );

  const handleLoginSuccess = () => {
    axios.get(`${API_URL}/profile`, { withCredentials: true })
      .then(res => {
        if (res.data.username) {
          setUsername(res.data.username);
        }
      });
    setShowModal(false);
    toast.success(`Welcome!`);
    setTimeout(() => window.scrollTo({ top: 0, behavior: "smooth" }), 300);
  };

  return (
    <div className={`full-page ${darkMode ? "dark-mode" : ""}`}>
      <ToastContainer position="top-right" autoClose={3000} />
      <Navbar />

      {/* Hero Section */}
      <motion.section
        className="hero parallax"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <div className="hero-content">
          <motion.h1 initial={{ y: 50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 1 }}>
            Predict Train Delays with Ease
          </motion.h1>
          <motion.p initial={{ y: 50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 1.2 }}>
            Stay ahead of schedule with AI-powered predictions
          </motion.p>
          {!auth && (
            <motion.button
              className="cta-btn"
              onClick={() => setShowModal(true)}
              whileHover={{ scale: 1.05 }}
            >
              Get Started
            </motion.button>
          )}
        </div>
      </motion.section>

      {/* --- Train Showcase Section --- */}
      <section className="train-showcase">
        <h2>🚄 Explore Our Trains</h2>
        <div className="train-cards">
          {[
            { name: "High-Speed", img: "/images/highspeed.jpg", desc: "Experience the future of travel." },
            { name: "Express", img: "/images/express.jpg", desc: "Fast & reliable long-distance service." },
            { name: "Regional", img: "/images/regional.jpg", desc: "Comfortable regional journeys." },
            { name: "Freight", img: "/images/freight.jpg", desc: "Efficient cargo transport." },
          ].map((train, idx) => (
            <div className="train-card" key={idx}>
              <img src={train.img} alt={train.name} />
              <h3>{train.name}</h3>
              <p>{train.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Prediction Section */}
      {auth && showPredictForm && (
        <section id="predict-section" className="predict-section">
          <motion.div
            className="predict-card"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2>Train Delay Prediction</h2>
            <form onSubmit={handleSubmit} className="prediction-form">
              <div className="input-group"><span>📅</span><input type="date" name="date" onChange={handleChange} required /></div>
              <div className="input-group"><span>🌡️</span><input type="number" name="temperature" placeholder="Temperature (°C)" onChange={handleChange} required /></div>
              <div className="input-group"><span>🌧️</span><input type="number" name="rain" min="0" max="1" placeholder="Rain (0 or 1)" onChange={handleChange} required /></div>
              <div className="input-group"><span>🌫️</span><input type="number" name="fog" min="0" max="1" placeholder="Fog (0 or 1)" onChange={handleChange} required /></div>
              <div className="input-group"><span>👁️</span><input type="number" name="visibility" placeholder="Visibility (m)" onChange={handleChange} required /></div>
              <div className="input-group"><span>💨</span><input type="number" name="windspeed" placeholder="Wind Speed (km/h)" onChange={handleChange} required /></div>
              <button type="submit" className="predict-btn">🚆 Predict Delay</button>
            </form>

            {/* Success Ticket Animation */}
            <AnimatePresence>
              {result !== null && (
                <motion.div
                  key="ticket"
                  className="ticket-result"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.8, opacity: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  🎟️ Predicted Delay: <span>{result} min</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </section>
      )}

      {/* History Section */}
      {auth && showHistory && (
        <section id="history-section" className="history-section">
          <h2>Your Prediction History</h2>
          {history.length === 0 ? (
            <p>No predictions yet.</p>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Date</th><th>Temp</th><th>Rain</th><th>Fog</th><th>Visib.</th><th>Wind</th><th>Delay</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item, idx) => (
                    <motion.tr key={idx} initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.05 }}>
                      <td>{item.date}</td>
                      <td>{item.temperature}</td>
                      <td>{item.rain}</td>
                      <td>{item.fog}</td>
                      <td>{item.visibility}</td>
                      <td>{item.windspeed}</td>
                      <td>{item.predicted_delay}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* --- Contact Section --- */}
      <section className="contact-section">
        <h2>📬 Contact Us</h2>
        <p>Have questions or suggestions? We'd love to hear from you!</p>
        <form className="contact-form">
          <input type="text" placeholder="Your Name" required />
          <input type="email" placeholder="Your Email" required />
          <textarea placeholder="Your Message" rows="4" required></textarea>
          <button type="submit">Send Message</button>
        </form>
      </section>

      {/* --- Footer -v-- */}
      <footer className="footer">
        <p>© 2025 Train Delay Predictor | All Rights Reserved</p>
        {/* --- Footer -v-- 
  <div className="social-links"> 
    <a href="https://www.linkedin.com/in/rishi-chaudhari-30133518b/" target="_blank" rel="noopener noreferrer">
      <FaLinkedin />
    </a>
    <a href="https://github.com/Rishi9911" target="_blank" rel="noopener noreferrer">
      <FaGithub />
    </a>
    <a href="mailto:rishichaudhari999@gmail.com">
      <MdEmail />
    </a>
  </div> */}
      </footer>

      {showModal && <AuthModal />}
    </div>
  );
}

export default App;
