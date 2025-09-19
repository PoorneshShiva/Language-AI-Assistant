import React, { useState, useEffect } from "react";
import Section from "./Section";
import DetectedCard from "./DetectedCard";
import WordCard from "./WordCard";
import * as api from '../api';

function itemKey(it) { return `${it.type}:${it.id}`; }

function Home({
  level,
  learnedKeys,
  reviewKeys,
  completedKeys,
  ignoredKeys,
  onStartTrain,
  onShuffleReview,
  onConfidence,
  onIgnore,
  stats,
}) {
  const [sentence, setSentence] = useState("");
  const [detected, setDetected] = useState([]); // [{type, id}]
  const [verbs, setVerbs] = useState([]);
  const [nouns, setNouns] = useState([]);

  useEffect(() => {
    async function fetchWords() {
      const words = await api.getWords('verb,noun', 1000);
      setVerbs(words.items.filter(item => item.type === 'verb'));
      setNouns(words.items.filter(item => item.type === 'noun'));
    }
    fetchWords();
  }, []);

  async function detectFromSentence() {
    const result = await api.detectWords(sentence, level, [...learnedKeys, ...reviewKeys, ...completedKeys, ...ignoredKeys]);
    setDetected(result.detected);
  }

  // Filter pick lists as well
  function availableVerbs() {
    const skip = new Set([...reviewKeys, ...completedKeys, ...ignoredKeys]);
    return verbs.filter((v) => !skip.has(itemKey({ type: "verb", id: v.id })));
  }
  function availableNouns() {
    const skip = new Set([...reviewKeys, ...completedKeys, ...ignoredKeys]);
    return nouns.filter((n) => !skip.has(itemKey({ type: "noun", id: n.id })));
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <Section title="Quick sentence" subtitle="Paste or type any German sentence. We'll detect words you can learn.">
              <textarea value={sentence} onChange={(e) => setSentence(e.target.value)} placeholder="e.g., Ich nehme den Käse und komme später." className="w-full border border-gray-300 rounded-lg px-4 py-3 h-24 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"></textarea>
              <div className="mt-4 flex gap-3">
                <button onClick={detectFromSentence} className="px-5 py-2 rounded-lg font-semibold bg-blue-600 text-white hover:bg-blue-700 shadow-md transform hover:-translate-y-1 transition-all">Detect words</button>
                <button onClick={() => { setSentence(""); setDetected([]); }} className="px-5 py-2 rounded-lg font-semibold bg-gray-200 text-gray-800 hover:bg-gray-300 shadow-md transform hover:-translate-y-1 transition-all">Clear</button>
              </div>
              {detected.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Detected words</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {detected.map((it) => (
                      <DetectedCard key={itemKey(it)} item={it} onStartTrain={onStartTrain} onConfidence={onConfidence} onIgnore={onIgnore} />
                    ))}
                  </div>
                </div>
              )}
            </Section>
          </div>

          <div className="space-y-6">
            <Section title="Stats" subtitle="Today & totals">
              <div className="flex justify-around items-center bg-white p-4 rounded-lg shadow-sm">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">{stats.today?.learned || 0}</div>
                  <div className="text-sm text-gray-500">Learned today</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-green-600">{stats.today?.practiced || 0}</div>
                  <div className="text-sm text-gray-500">Practiced today</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-purple-600">{stats.today?.completed || 0}</div>
                  <div className="text-sm text-gray-500">Completed today</div>
                </div>
              </div>
            </Section>

            <Section title="Review" subtitle="Refresh your memory">
              <button onClick={onShuffleReview} className="w-full px-5 py-3 rounded-lg font-semibold bg-green-600 text-white hover:bg-green-700 shadow-md transform hover:-translate-y-1 transition-all">Shuffle review ({reviewKeys.size} words)</button>
            </Section>
          </div>
        </div>

        <div className="mt-6">
          <Section title="Pick a word" subtitle="Manual selection. Choosing a confidence will file it into Review or Completed and hide it from this list.">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Verbs</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availableVerbs().map((v) => (
                    <WordCard key={v.id} item={{ type: "verb", id: v.id }} title={v.id} subtitle="" onStartTrain={onStartTrain} onConfidence={onConfidence} onIgnore={onIgnore} />
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Nouns</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availableNouns().map((n) => (
                    <WordCard key={n.id} item={{ type: "noun", id: n.id }} title={n.id} subtitle="" onStartTrain={onStartTrain} onConfidence={onConfidence} onIgnore={onIgnore} isMastered={completedKeys.has(itemKey({ type: "noun", id: n.id }))} />
                  ))}
                </div>
              </div>
            </div>
          </Section>
        </div>
      </div>
    </div>
  );
}

export default Home;