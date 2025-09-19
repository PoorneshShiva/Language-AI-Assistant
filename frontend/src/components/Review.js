import React, { useState } from 'react';
import Section from "./Section";

function Review({ queue, onUpdate }) {
  const [current, setCurrent] = useState(0);
  const item = queue[current];
  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6 space-y-6">
      <Section title="Review mode" subtitle="Mixed items from learned words">
        {queue.length === 0 ? (
          <div className="text-sm text-gray-600">No items due. Add some words to review.</div>
        ) : (
          <div className="space-y-3">
            <div className="text-sm">Item {current + 1} of {queue.length}</div>
            <div className="border border-dashed border-gray-300 rounded-xl p-6 text-center text-gray-600">
              <div className="mb-2">{item.type === "verb" ? "Verb" : "Noun"}: <span className="font-medium">{item.id}</span></div>
              <div className="text-xs">Wireframe placeholder — show a quick prompt or flashcard here.</div>
            </div>
            <div className="flex gap-2">
              {["Practice", "Difficult", "Got It", "Mastered"].map((b) => (
                <button key={b} onClick={() => { onUpdate(item, b); setCurrent((c) => Math.min(queue.length - 1, c + 1)); }} className="px-3 py-2 rounded-xl border border-gray-300 hover:bg-gray-50">{b}</button>
              ))}
            </div>
          </div>
        )}
      </Section>
    </div>
  );
}

export default Review;
