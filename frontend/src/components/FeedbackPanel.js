import React from 'react';

function FeedbackPanel({ result }) {
  if (!result) return null;
  return (
    <div className={`rounded-xl p-3 border ${result.correct ? "border-green-300 bg-green-50" : "border-red-300 bg-red-50"}`}>
      <div className="font-medium">{result.correct ? "Correct" : "Try again"}</div>
      {!result.correct && (<div className="text-sm mt-1">Primary fix: <span className="font-medium">{result.primaryFix}</span></div>)}
      <div className="text-xs text-gray-700 mt-1">{result.why}</div>
    </div>
  );
}

export default FeedbackPanel;
