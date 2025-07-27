import React, { useEffect, useState } from "react";
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;


const CommentSection = ({ symbol }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [replyTo, setReplyTo] = useState(null);
  const [message, setMessage] = useState("");
  const username = localStorage.getItem("username");
  const currentRole = localStorage.getItem("role");

  const fetchComments = async () => {
    const res = await fetch(`${BACKEND_URL}/api/comments/${symbol}`);
    const data = await res.json();
    const enriched = data.map(comment => ({
      ...comment,
      liked_by_user: (comment.likers || []).includes(username),
    }));
    setComments(enriched);
  };

  const handleLike = async (id) => {
    const res = await fetch(`${BACKEND_URL}/api/comments/${symbol}/${id}/like`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    const data = await res.json();
    if (res.ok) fetchComments();
    else setMessage(`❌ ${data.error}`);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bu yorumu silmek istediğinize emin misiniz?")) return;
    const res = await fetch(`${BACKEND_URL}/api/comments/${symbol}/${id}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    const data = await res.json();
    if (res.ok) {
      setMessage("🗑️ Yorum silindi");
      fetchComments();
    } else {
      setMessage(`❌ ${data.error}`);
    }
  };

  const handleSubmit = async () => {
    if (!newComment.trim()) return;
    const res = await fetch(`${BACKEND_URL}/api/comments/${symbol}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        comment: newComment,
        parent_id: replyTo || null,
      }),
    });
    const data = await res.json();
    if (res.ok) {
      setMessage("✅ Yorum eklendi!");
      setNewComment("");
      setReplyTo(null);
      fetchComments();
    } else {
      setMessage(`❌ ${data.error}`);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [symbol]);

  const renderCommentText = (text) => {
    const parts = text.split(/(@\w+)/g);
    return parts.map((part, i) =>
      part.startsWith("@") ? (
        <span key={i} className="text-blue-500 font-semibold">{part}</span>
      ) : (
        <span key={i}>{part}</span>
      )
    );
  };

  const renderRoleBadge = (role) => {
    if (role === "admin") {
      return <span className="bg-green-600 text-white text-[10px] px-1.5 py-0.5 rounded-md mr-1">CRE</span>;
    }
    if (role === "mod") {
      return <span className="bg-gray-500 text-white text-[10px] px-1.5 py-0.5 rounded-md mr-1">MOD</span>;
    }
    if (role === "gold") {
      return <span className="bg-yellow-400 text-black text-[10px] px-1.5 py-0.5 rounded-md mr-1">GOLD</span>;
    }
    return null;
  };

  const renderReplies = (replies) => (
    <ul className="ml-8 mt-2 space-y-2">
      {replies.map(reply => (
        <li key={reply.id} className="bg-gray-200 dark:bg-gray-600 p-2 rounded">
          <div className="flex justify-between items-center mb-1">
            <strong>
              {renderRoleBadge(reply.role)}
              {reply.username}
            </strong>
            {(reply.username === username || ["admin", "mod"].includes(currentRole)) && (
              <button
                onClick={() => handleDelete(reply.id)}
                className="text-red-500 text-xs hover:underline"
              >
                Sil
              </button>
            )}
          </div>
          <p className="text-sm">{renderCommentText(reply.comment)}</p>
          <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
            <span>{new Date(reply.timestamp).toLocaleString("tr-TR")}</span>
            <button
              onClick={() => handleLike(reply.id)}
              className="hover:underline text-blue-600"
            >
              {reply.liked_by_user ? "👎 Beğeniyi Geri Al" : "👍 Beğen"} ({reply.likes || 0})
            </button>
          </div>
        </li>
      ))}
    </ul>
  );

  return (
    <div className="mt-8 p-4 bg-white dark:bg-gray-800 rounded shadow">
      <h3 className="text-lg font-semibold mb-2">💬 Yorumlar</h3>
      {comments.length === 0 && <p>Henüz yorum yok.</p>}

      <ul className="mb-4 space-y-4">
        {comments.map((c) => (
          <li key={c.id} className="flex items-start gap-3 bg-gray-100 dark:bg-gray-700 p-3 rounded-lg shadow-sm">
            <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold text-lg">
              {c.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <strong>
                  {renderRoleBadge(c.role)}
                  {c.username}
                </strong>
                {(c.username === username || ["admin", "mod"].includes(currentRole)) && (
                  <button
                    onClick={() => handleDelete(c.id)}
                    className="text-red-500 text-xs hover:underline ml-4"
                  >
                    Sil
                  </button>
                )}
              </div>
              <p className="text-sm leading-snug break-words relative">
                {renderCommentText(c.comment)}
                <span className="absolute right-0 bottom-0 text-[10px] text-gray-400">
                  {new Date(c.timestamp).toLocaleString("tr-TR")}
                </span>
              </p>
              <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                <button
                  onClick={() => handleLike(c.id)}
                  className="hover:underline text-blue-600"
                >
                  {c.liked_by_user ? "👎 Beğeniyi Geri Al" : "👍 Beğen"} ({c.likes || 0})
                </button>
                <button
                  onClick={() => {
                    setReplyTo(c.id);
                    setNewComment(`@${c.username} `);
                  }}
                  className="hover:underline text-green-600"
                >
                  Yanıtla
                </button>
              </div>
              {c.replies && renderReplies(c.replies)}
            </div>
          </li>
        ))}
      </ul>

      {username ? (
        <>
          {replyTo && (
            <p className="text-xs mb-1">
              ✍️ <strong>Yanıtlanan yorum ID:</strong> {replyTo}{" "}
              <button onClick={() => setReplyTo(null)} className="text-red-400 ml-2 text-xs hover:underline">
                İptal Et
              </button>
            </p>
          )}
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Yorumunuzu yazın (max 300 karakter)"
            maxLength={300}
            className="w-full p-2 border rounded mb-2 text-black"
          />
          <button
            onClick={handleSubmit}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Yorum Yap
          </button>
          <p className="text-sm mt-2">{message}</p>
        </>
      ) : (
        <p className="text-sm text-gray-500">Yorum yapmak için giriş yapmalısınız.</p>
      )}
    </div>
  );
};

export default CommentSection;
