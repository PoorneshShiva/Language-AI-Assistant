import React, { useState } from "react";
import { ARTICLE_STYLE } from "../constants";
import Section from "./Section";
import CaseTable from "./CaseTable";
import FeedbackPanel from "./FeedbackPanel";
import * as api from "../api";

function NounTrainer({ noun, level, onAddToReview }) {
  const [mode, setMode] = useState(level === "beginner" ? "article" : "article+case");
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const style = ARTICLE_STYLE[noun.gender.toLowerCase()];

  async function evaluate() {
    const evaluation = await api.evaluate({type: 'noun', id: noun.noun}, '', noun.caseForms.accusative, input, level);
    setResult(evaluation);
  }

  return (
    <Section title={`Noun · ${noun.noun}`} subtitle={noun.english_translation}
      right={<button onClick={() => onAddToReview({ type: "noun", id: noun.noun })} className="px-3 py-1.5 rounded-xl border border-gray-300">Add to review</button>}>
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2 py-0.5 rounded ${style.badge}`}>{style.icon} {style.label}</span>
        <span className={`px-2 py-0.5 rounded border ${style.border} text-xs`}>Plural: {noun.plural}</span>
      </div>
      <CaseTable noun={noun} />
      <div className="mt-6">
        <h3 className="font-semibold mb-2">Practice</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {[{ id: "article", label: "Article only" }, { id: "article+case", label: "Article plus case" }].map((o) => (
            <button key={o.id} onClick={() => setMode(o.id)} className={`px-3 py-2 rounded-xl border ${mode === o.id ? "border-gray-900 bg-gray-900 text-white" : "border-gray-300"}`}>{o.label}</button>
          ))}
        </div>
        <div className="text-sm">Question: What is the Accusative singular article for <span className="font-medium">{noun.noun}</span>?</div>
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type der, die, das, den, dem, des..." className="w-full border border-gray-300 rounded-xl px-3 py-2 font-mono mt-2" />
        <div className="mt-3 flex items-center gap-2">
          <button onClick={evaluate} className="px-4 py-2 rounded-xl border border-gray-900 bg-gray-900 text-white">Check</button>
          <button onClick={() => { setInput(""); setResult(null); }} className="px-4 py-2 rounded-xl border border-gray-300">Clear</button>
        </div>
        <div className="mt-3"><FeedbackPanel result={result} /></div>
      </div>
    </Section>
  );
}

export default NounTrainer;
