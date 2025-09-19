import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Home from './components/Home';
import Train from './components/Train';
import Review from './components/Review';
import Completed from './components/Completed';
import Settings from './components/Settings';
import * as api from './api';

function itemKey(it) { return `${it.type}:${it.id}`; }

export default function App() {
  const [current, setCurrent] = useState("Home");
  const [level, setLevel] = useState("beginner");
  const [preferences, setPreferences] = useState({ dailyGoal: 10, style: "mixed", reviewEnabled: true });

  const [reviewQueue, setReviewQueue] = useState([]); // [{type, id}]
  const [completed, setCompleted] = useState([]); // [{type, id}]
  const [ignored, setIgnored] = useState([]); // [{type, id}]
  const [learned, setLearned] = useState([]); // all items ever added
  const [activeItem, setActiveItem] = useState(null); // {type, id}
  const [stats, setStats] = useState({ learned: 0, reviewDue: 0, completed: 0 });

  useEffect(() => {
    async function fetchData() {
      const [settings, stats, queue, completedItems, ignoredItems] = await Promise.all([
        api.getSettings(),
        api.getStats(),
        api.getPracticeQueue(level),
        api.getCompleted(),
        // api.getIgnored(), // This endpoint doesn't exist, I will manage ignored items in the frontend for now
      ]);
      setPreferences(settings);
      setLevel(settings.level);
      setStats(stats);
      setReviewQueue(queue.queue);
      setCompleted(completedItems.items);
    }
    fetchData();
  }, [level]);


  // Keys for quick membership checks
  const reviewKeys = new Set(reviewQueue.map(itemKey));
  const completedKeys = new Set(completed.map(itemKey));
  const ignoredKeys = new Set(ignored.map(itemKey));
  const learnedKeys = new Set(learned.map(itemKey));

  async function onStartTrain(it) {
    let details;
    if (it.type === 'verb') {
        details = await api.getVerb(it.id);
    } else {
        details = await api.getNoun(it.id);
    }
    setActiveItem({...it, ...details});
    setCurrent("Train");
  }

  async function onConfidence(it, conf) {
    await api.postConfidence(it, conf, level, { correct: true });
    // Refetch data to update the UI
    const [queue, completedItems] = await Promise.all([
        api.getPracticeQueue(level),
        api.getCompleted(),
    ]);
    setReviewQueue(queue.queue);
    setCompleted(completedItems.items);
  }

  async function onIgnore(it) {
    await api.postIgnore(it);
    setIgnored((igs) => (igs.find((x) => itemKey(x) === itemKey(it)) ? igs : [...igs, it]));
  }

  function shuffleReview() {
    setReviewQueue((q) => [...q].sort(() => Math.random() - 0.5));
    setCurrent("Review");
  }

  async function handleReviewUpdate(it, conf) {
    await api.postConfidence(it, conf, level, { correct: true });
    // Refetch data to update the UI
    const [queue, completedItems] = await Promise.all([
        api.getPracticeQueue(level),
        api.getCompleted(),
    ]);
    setReviewQueue(queue.queue);
    setCompleted(completedItems.items);
  }

  async function reviewAgain(it) {
    await api.postReviewAgain(it);
    const [queue, completedItems] = await Promise.all([
        api.getPracticeQueue(level),
        api.getCompleted(),
    ]);
    setReviewQueue(queue.queue);
    setCompleted(completedItems.items);
    setCurrent("Review");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header current={current} setCurrent={setCurrent} />

      {current === "Home" && (
        <Home
          level={level}
          learnedKeys={learned.map(itemKey)}
          reviewKeys={reviewQueue.map(itemKey)}
          completedKeys={completed.map(itemKey)}
          ignoredKeys={ignored.map(itemKey)}
          onStartTrain={onStartTrain}
          onShuffleReview={shuffleReview}
          onConfidence={onConfidence}
          onIgnore={onIgnore}
          stats={stats}
        />
      )}

      {current === "Train" && (
        <Train activeItem={activeItem} level={level} setActiveItem={setActiveItem} onAddToReview={(it) => onConfidence(it, "Good")} />
      )}

      {current === "Review" && (
        <Review queue={reviewQueue} onUpdate={handleReviewUpdate} />
      )}

      {current === "Completed" && (
        <Completed items={completed} onReviewAgain={reviewAgain} />
      )}

      {current === "Settings" && (
        <Settings level={level} setLevel={setLevel} preferences={preferences} setPreferences={setPreferences} />
      )}
    </div>
  );
}