import React from 'react';
import Section from "./Section";
import VerbTrainer from "./VerbTrainer";
import NounTrainer from "./NounTrainer";

function Train({ activeItem, level, setActiveItem, onAddToReview }) {
  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6 space-y-6">
      {!activeItem ? (
        <Section title="Trainer" subtitle="Pick a word on Home to start.">
          <button onClick={() => setActiveItem({})} className="hidden" />
          <div className="text-sm text-gray-600">No selection yet. Go to Home and choose a word to train.</div>
        </Section>
      ) : activeItem.type === "verb" ? (
        <VerbTrainer level={level} verb={activeItem} onAddToReview={onAddToReview} />
      ) : (
        <NounTrainer level={level} noun={activeItem} onAddToReview={onAddToReview} />
      )}
    </div>
  );
}

export default Train;
