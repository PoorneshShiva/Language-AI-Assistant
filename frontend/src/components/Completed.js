import React from 'react';
import Section from "./Section";

function itemKey(it) { return `${it.type}:${it.id}`; }

function Completed({ items, onReviewAgain }) {
  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6 space-y-6">
      <Section title="Completed" subtitle="Mastered items you can revisit.">
        {items.length === 0 ? (
          <div className="text-sm text-gray-600">Nothing here yet. Mark items as Easy to complete them.</div>
        ) : (
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-2">
            {items.map((it) => (
              <div key={itemKey(it)} className="border border-gray-300 rounded-xl p-3 flex items-center justify-between">
                <div>{it.type === "verb" ? "Verb" : "Noun"}: <span className="font-medium">{it.id}</span></div>
                <button onClick={() => onReviewAgain(it)} className="px-3 py-1.5 rounded-xl border border-gray-300">Review again</button>
              </div>
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}

export default Completed;
