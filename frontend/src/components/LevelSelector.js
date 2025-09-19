import React from 'react';

function LevelSelector({ level, setLevel }) {
  const options = [
    { id: "beginner", label: "Beginner (A1 to A2)" },
    { id: "advanced", label: "Advanced (A2 to B2)" },
  ];
  return (
    <div className="flex flex-col sm:flex-row gap-2">
      {options.map((o) => (
        <button key={o.id} onClick={() => setLevel(o.id)} className={`px-4 py-2 rounded-xl border ${level === o.id ? "border-gray-900 bg-gray-900 text-white" : "border-gray-300 bg-white hover:bg-gray-50"}`}>{o.label}</button>
      ))}
    </div>
  );
}

export default LevelSelector;
