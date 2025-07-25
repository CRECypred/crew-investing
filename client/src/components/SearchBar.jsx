import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const SearchBar = () => {
  const [inputValue, setInputValue] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (inputValue.length < 2) {
      setSuggestions([]);
      return;
    }
    fetch(`http://localhost:5000/api/symbols?q=${inputValue}`)
      .then((res) => res.json())
      .then((data) => setSuggestions(data))
      .catch((err) => console.error("Autocomplete hatası:", err));
  }, [inputValue]);

  const handleSelectSymbol = (symbol) => {
    let sym = symbol.toUpperCase();
    if (!sym.includes(".") && !sym.includes("=")) {
      sym += ".IS";
    }
    navigate(`/stock/${sym}`);
    setSuggestions([]);
    setInputValue("");
  };

  return (
    <div className="flex justify-center mb-6 relative">
      <div className="relative w-64">
        <input
          type="text"
          autoComplete="off"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && inputValue.trim()) {
              handleSelectSymbol(inputValue.trim());
            }
          }}
          className="border rounded px-4 py-2 w-full text-center text-sm focus:outline-none focus:ring bg-white dark:bg-neutral-800 text-black dark:text-white"
          placeholder="Sembol girin (örn: THYAO veya USDTRY=X)"
        />
        {suggestions.length > 0 && (
          <ul className="absolute z-10 mt-1 w-full bg-white dark:bg-neutral-800 border border-gray-300 dark:border-gray-600 rounded shadow text-left text-sm max-h-52 overflow-y-auto">
            {suggestions.map((symbol, i) => (
              <li
                key={i}
                onClick={() => handleSelectSymbol(symbol)}
                className="px-4 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700"
              >
                {symbol}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SearchBar;
