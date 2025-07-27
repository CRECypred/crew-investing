import React from "react";
import { Link } from "react-router-dom";

const ListelerPage = () => {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">Sinyal Grupları</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

        {/* First Group: MA */}
        <Link
          to="/listeler/ma"
          className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 hover:shadow-md transition"
        >
          <h2 className="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-200">MA Sinyalleri</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            MA(8/22), MA(22/50), MA(50/200) kesişimlerine göre AL/SAT sinyalleri.
          </p>
        </Link>

        {/* Second Group: MACD, Trendline, MOST */}
        <Link
          to="/listeler/second"
          className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 hover:shadow-md transition"
        >
          <h2 className="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-200">MACD, Trendline, MOST</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            MACD, Trendline ve MOST tabanlı teknik sinyaller.
          </p>
        </Link>

        {/* Third Group: MOST EMA, Old School */}
        <Link
          to="/listeler/third"
          className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 hover:shadow-md transition"
        >
          <h2 className="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-200">MOST EMA & Old School</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            MOST EMA ve klasik (Old School) kesişim sinyalleri.
          </p>
        </Link>
      </div>
    </div>
  );
};

export default ListelerPage;
