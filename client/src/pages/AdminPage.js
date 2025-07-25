import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AdminPage = () => {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");
  const role = localStorage.getItem("role");

  useEffect(() => {
    if (role !== "admin") {
      alert("Bu sayfa sadece adminlere özeldir.");
      navigate("/"); // Anasayfaya yönlendir
    }
  }, [role, navigate]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🛠️ Admin Paneli</h1>
      <p>Hoş geldin, <strong>{username}</strong> 👑</p>

      <div className="mt-4 space-y-2">
        <p>- Kullanıcıları görüntüleme</p>
        <p>- Yorumları silme yetkisi</p>
        <p>- Sistem raporları</p>
        <p>- (İleride) Yeni kullanıcı oluşturma</p>
      </div>
    </div>
  );
};

export default AdminPage;
