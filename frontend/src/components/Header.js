import React from 'react';

function Header({ current, setCurrent }) {
  const tabs = ["Home", "Train", "Review", "Completed", "Settings"];
  return (
    <header className="sticky top-0 z-50 bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex-shrink-0">
            <h1 className="text-2xl font-bold text-gray-800">German AI Assistant</h1>
          </div>
          <nav className="hidden md:flex md:space-x-8">
            {tabs.map((t) => (
              <button
                key={t}
                onClick={() => setCurrent(t)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  current === t
                    ? "bg-blue-600 text-white"
                    : "text-gray-700 hover:bg-gray-200"
                }`}>
                {t}
              </button>
            ))}
          </nav>
          <div className="md:hidden"> {/* Mobile menu button */}
            {/* You can add a mobile menu button here if needed */}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;