import React from 'react';

function Toggle({ checked, onChange, label }) {
  return (
    <label className="inline-flex items-center gap-2 cursor-pointer select-none">
      <span className="text-sm text-gray-700">{label}</span>
      <span className={`w-10 h-6 flex items-center rounded-full p-0.5 ${checked ? "bg-gray-900" : "bg-gray-300"}`} onClick={() => onChange(!checked)}>
        <span className={`h-5 w-5 bg-white rounded-full transform transition ${checked ? "translate-x-4" : "translate-x-0"}`} />
      </span>
    </label>
  );
}

export default Toggle;
