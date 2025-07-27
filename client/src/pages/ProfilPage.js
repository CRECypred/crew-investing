import React, { useEffect, useState } from "react";
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ProfilePage = () => {
  const [userData, setUserData] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});
  const username = localStorage.getItem("username");

  useEffect(() => {
    if (!username) return;

    fetch(`${BACKEND_URL}/api/user/${username}`)
      .then((res) => res.json())
      .then((data) => {
        setUserData(data);
        setEditedData({ full_name: data.full_name, email: data.email });
      })
      .catch((err) => console.error("Kullanıcı bilgisi alınamadı", err));
  }, [username]);

  const handleAvatarChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleAvatarUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return alert("Lütfen bir dosya seçin.");

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("username", username);

    const res = await fetch("${BACKEND_URL}/api/upload-avatar", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (res.ok) {
      alert("✅ Profil fotoğrafı güncellendi!");
      setUserData((prev) => ({ ...prev, avatar_url: data.avatar_url }));
    } else {
      alert(`❌ ${data.error}`);
    }
  };

  const handleProfileUpdate = async () => {
    const res = await fetch("${BACKEND_URL}/api/update-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: userData.username,
        full_name: editedData.full_name,
        email: editedData.email,
      }),
    });

    const result = await res.json();
    if (res.ok) {
      alert("✅ Bilgiler güncellendi!");
      setUserData((prev) => ({
        ...prev,
        full_name: editedData.full_name,
        email: editedData.email,
      }));
      setIsEditing(false);
    } else {
      alert(`❌ ${result.error}`);
    }
  };

  if (!userData) {
    return <p className="text-center mt-10">Kullanıcı bilgileri yükleniyor...</p>;
  }

  return (
    <div className="max-w-3xl mx-auto mt-10 p-6 bg-white dark:bg-gray-800 shadow rounded-lg">
      <h1 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">Profil</h1>

      <div className="flex items-start gap-8">
        {/* Sol: Profil Resmi ve Yükleme */}
        <div className="flex flex-col items-center gap-4">
          <img
            src={
                userData && userData.avatar_url
                    ? `${process.env.REACT_APP_API_URL}${userData.avatar_url}`
                    : `${process.env.REACT_APP_API_URL}/static/avatars/default.png`
            }
            alt="Profil"
            className="w-28 h-28 rounded-full border-4 border-gray-300 object-cover"
          />

          <form onSubmit={handleAvatarUpload} className="flex flex-col items-center gap-2">
            <label
              htmlFor="avatarUpload"
              className="bg-blue-600 text-white px-3 py-1 rounded cursor-pointer hover:bg-blue-700 text-sm"
            >
              Profil Fotoğrafını Değiştir
            </label>
            <input
              id="avatarUpload"
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              className="hidden"
            />
            <button
              type="submit"
              className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-sm"
            >
              Fotoğrafı Yükle
            </button>
          </form>
        </div>

        {/* Sağ: Bilgiler */}
        <div className="flex flex-col justify-center gap-2">
          {isEditing ? (
            <>
              <input
                type="text"
                className="p-2 rounded border dark:bg-gray-700 text-gray-800 dark:text-white"
                value={editedData.full_name}
                onChange={(e) =>
                  setEditedData((prev) => ({ ...prev, full_name: e.target.value }))
                }
              />
              <input
                type="email"
                className="p-2 rounded border dark:bg-gray-700 text-gray-800 dark:text-white"
                value={editedData.email}
                onChange={(e) =>
                  setEditedData((prev) => ({ ...prev, email: e.target.value }))
                }
              />
              <div className="flex gap-2 mt-2">
                <button
                  className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-sm"
                  onClick={handleProfileUpdate}
                >
                  Kaydet
                </button>
                <button
                  className="bg-gray-400 text-white px-3 py-1 rounded hover:bg-gray-500 text-sm"
                  onClick={() => {
                    setIsEditing(false);
                    setEditedData({ full_name: userData.full_name, email: userData.email });
                  }}
                >
                  İptal
                </button>
              </div>
            </>
          ) : (
            <>
              <p className="text-xl font-semibold text-gray-800 dark:text-white">
                Ad Soyad: <span className="font-bold">{userData.full_name}</span>
              </p>
              <p className="text-lg text-gray-700 dark:text-gray-300">
                E-posta: <span>{userData.email}</span>
              </p>
              <button
                className="mt-2 bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-sm w-fit"
                onClick={() => setIsEditing(true)}
              >
                Bilgileri Güncelle
              </button>
            </>
          )}

          <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
            Kullanıcı Adı: <span>{userData.username}</span>
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Rol: <span className="uppercase">{userData.role}</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
