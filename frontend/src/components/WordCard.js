import React from 'react';
import Pill from "./Pill";

function WordCard({ item, title, subtitle, onStartTrain, onConfidence, onIgnore, badges = [], articleStyle, isMastered }) {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex flex-col justify-between transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${articleStyle ? articleStyle.border : ""}`}>
      <div>
        <div className="flex items-center gap-2 mb-2">
          {articleStyle && <span className={`px-2 py-1 rounded-full text-xs font-semibold ${articleStyle.badge}`}>{articleStyle.icon} {articleStyle.label}</span>}
          <div className="font-bold text-lg text-gray-800">{title}</div>
        </div>
        <div className="text-sm text-gray-500">{subtitle}</div>
        <div className="mt-2 flex gap-1 flex-wrap">{badges.map((b, i) => (<Pill key={i}>{b}</Pill>))}</div>
      </div>
      {isMastered ? (
        <div className="mt-4 text-center text-gray-500 font-semibold">Already Mastered</div>
      ) : (
        <>
          <div className="mt-4 flex flex-wrap gap-2">
            <button onClick={() => onStartTrain(item)} className="flex-grow px-3 py-2 text-sm font-semibold rounded-md bg-blue-500 text-white hover:bg-blue-600 transition-colors">Train</button>
            <button onClick={() => onIgnore(item)} className="px-3 py-2 text-sm font-semibold rounded-md bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors">Ignore</button>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {["Practice", "Difficult", "Got It", "Mastered"].map((b) => (
              <button key={b} onClick={() => onConfidence(item, b)} className="flex-grow px-3 py-1.5 text-xs font-semibold rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors">{b}</button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default WordCard;
