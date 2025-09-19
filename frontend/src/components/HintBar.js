import React from 'react';

function HintBar({ nounHints, onInsert }) {
  return (
    <div className="flex flex-wrap gap-2">
      {nounHints.map((h) => (
        <button key={h.label} onClick={() => onInsert(h.insert)} className="px-2 py-1 rounded-full border border-gray-300 text-xs bg-white hover:bg-gray-50">{h.label}</button>
      ))}
    </div>
  );
}

export default HintBar;
