import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RegisterPage = () => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    const res = await fetch("${BACKEND_URL}/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: fullName, email, username, password }),
    });

    const data = await res.json();

    if (res.ok) {
      setMessage("✅ Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...");
      setFullName("");
      setEmail("");
      setUsername("");
      setPassword("");
      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } else {
      setMessage(`❌ ${data.error || "Kayıt başarısız"}`);
    }
  };

  return (
    <form onSubmit={handleRegister} className="max-w-md mx-auto mt-10 bg-white dark:bg-gray-800 p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Kayıt Ol</h2>

      <input
        type="text"
        placeholder="Ad Soyad"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        className="w-full mb-3 p-2 border rounded"
        required
      />
      <input
        type="email"
        placeholder="E-posta"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full mb-3 p-2 border rounded"
        required
      />
      <input
        type="text"
        placeholder="Kullanıcı Adı"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="w-full mb-3 p-2 border rounded"
        required
      />
      <input
        type="password"
        placeholder="Şifre"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full mb-4 p-2 border rounded"
        required
      />
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
      >
        Kayıt Ol
      </button>
      <p className="mt-4 text-sm text-red-600 dark:text-red-400">{message}</p>
    </form>
  );
};

export default RegisterPage;
