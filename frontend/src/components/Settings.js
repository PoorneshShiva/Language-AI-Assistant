import React, { useState, useEffect } from 'react';
import Section from "./Section";
import LevelSelector from "./LevelSelector";
import Toggle from "./Toggle";

function Settings({ level, setLevel, preferences, setPreferences }) {
  const [goal, setGoal] = useState(preferences.dailyGoal || 10);

  useEffect(() => { setPreferences({ ...preferences, dailyGoal: goal }); }, [goal]);

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6 space-y-6">
      <Section title="Level">
        <LevelSelector level={level} setLevel={setLevel} />
      </Section>
      <Section title="Daily goal" subtitle="How many items do you want to practice each day?">
        <div className="flex items-center gap-3">
          {[5, 10, 20].map((n) => (
            <button key={n} onClick={() => setGoal(n)} className={`px-3 py-2 rounded-xl border ${goal === n ? "border-gray-900 bg-gray-900 text-white" : "border-gray-300 hover:bg-gray-50"}`}>{n}</button>
          ))}
          <div className="text-sm text-gray-600">Current: {goal}</div>
        </div>
      </Section>
      <Section title="Learning style" subtitle="Pick what suits you best.">
        <div className="flex flex-wrap gap-2">
          {[
            { id: "reading", label: "Reading" },
            { id: "visual", label: "Visual" },
            { id: "mixed", label: "Mixed" },
          ].map((o) => (
            <button key={o.id} onClick={() => setPreferences({ ...preferences, style: o.id })} className={`px-4 py-2 rounded-xl border ${preferences.style === o.id ? "border-gray-900 bg-gray-900 text-white" : "border-gray-300 bg-white hover:bg-gray-50"}`}>{o.label}</button>
          ))}
        </div>
      </Section>
      <Section title="Review queue">
        <Toggle checked={preferences.reviewEnabled} onChange={(v) => setPreferences({ ...preferences, reviewEnabled: v })} label="Enable review queue" />
      </Section>
    </div>
  );
}

export default Settings;
