import React, { useMemo, useState, useEffect } from "react";
import { ARTICLE_STYLE } from "../constants";
import Section from "./Section";
import Pill from "./Pill";
import ConjugationTable from "./ConjugationTable";
import FeedbackPanel from "./FeedbackPanel";
import HintBar from "./HintBar";
import * as api from "../api";

function VerbTrainer({ level, verb, onAddToReview }) {
  const [trainingData, setTrainingData] = useState(null); // Stores VerbTrainingData
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [nounHints, setNounHints] = useState([]);

  useEffect(() => {
    async function fetchTrainingData() {
        const data = await api.getPrompts('verb', verb.infinitive, level, 1);
        setTrainingData(data.prompts[0]); // Assuming getPrompts returns a list with VerbTrainingData as the first item
    }
    async function fetchHints() {
        const hints = await api.getHints('all', 'accusative,dative', 20);
        setNounHints(hints.hints);
    }
    fetchTrainingData();
    fetchHints();
    setInput("");
    setResult(null);
  }, [verb, level]);

  async function evaluate() {
    if (!trainingData) return;
    const evaluation = await api.evaluate({type: 'verb', id: verb.infinitive}, trainingData.id, trainingData.de, input, level);
    setResult(evaluation);
  }

  return (
    <Section title={`Verb · ${verb.infinitive}`} subtitle={verb.english_alternative.join(", ")}
      right={<button onClick={() => onAddToReview({ type: "verb", id: verb.infinitive })} className="px-3 py-1.5 rounded-xl border border-gray-300">Add to review</button>}>
      {trainingData && (
        <div className="space-y-3">
          <div className="text-sm text-gray-700 flex flex-wrap gap-2">
            {trainingData.is_separable && <Pill>separable</Pill>}
            {!trainingData.is_regular && <Pill>irregular</Pill>}
          </div>
          <ConjugationTable verb={trainingData.conjugations} level={level} />
          <div className="text-sm text-gray-600">{trainingData.notes.map((n, i) => (<div key={i}>• {n}</div>))}</div>
        </div>
      )}
      <div className="mt-6">
        <h3 className="font-semibold mb-2">Drill</h3>
        <div className="mb-3 text-sm">Prompt: <span className="font-medium">{trainingData?.en}</span></div>
        <input value={input} onChange={(e) => setInput(e.target.value)} className="w-full border border-gray-300 rounded-xl px-3 py-2 font-mono" placeholder="Type your German sentence" />
        <div className="mt-3 flex items-center gap-2">
          <button onClick={evaluate} className="px-4 py-2 rounded-xl border border-gray-900 bg-gray-900 text-white">Check</button>
          <button onClick={() => { setInput(""); setResult(null); }} className="px-4 py-2 rounded-xl border border-gray-300 bg-white">Clear</button>
        </div>
        <div className="mt-3"><FeedbackPanel result={result} /></div>
        <div className="mt-4"><div className="text-sm font-medium mb-1">Hints</div><HintBar nounHints={nounHints} onInsert={(w) => setInput((s) => (s ? s + " " + w : w))} /></div>
      </div>
    </Section>
  );
}

export default VerbTrainer;