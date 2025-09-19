import React, { useEffect, useMemo, useState } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import SentenceLab from './components/SentenceLab';
import AssignmentBoard from './components/AssignmentBoard';
import ScenarioTrainer from './components/ScenarioTrainer';
import {
  getStats,
  getSettings,
  analyzeSentence,
  createAssignment,
  listAssignments,
  updateAssignment,
  createScenario,
  listScenarios,
  listAnalyses,
} from './api';

const VIEWS = {
  DASHBOARD: 'Dashboard',
  SENTENCE: 'Sentence Lab',
  ASSIGNMENTS: 'Assignments',
  SCENARIOS: 'Scenarios',
};

export default function App() {
  const [currentView, setCurrentView] = useState(VIEWS.DASHBOARD);
  const [stats, setStats] = useState(null);
  const [settings, setSettings] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const level = settings?.level || 'beginner';

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true);
        const [statsData, settingsData, assignmentsData, scenariosData, analysesData] = await Promise.all([
          getStats(),
          getSettings(),
          listAssignments(),
          listScenarios(),
          listAnalyses(),
        ]);
        setStats(statsData);
        setSettings(settingsData);
        setAssignments(assignmentsData);
        setSelectedAssignment(assignmentsData[0] || null);
        setScenarios(scenariosData);
        setAnalysisHistory(analysesData);
        setCurrentAnalysis(analysesData[0] || null);
      } catch (err) {
        setError(err.message || 'Unbekannter Fehler beim Laden');
      } finally {
        setLoading(false);
      }
    }
    bootstrap();
  }, []);

  const refreshStats = async () => {
    try {
      const fresh = await getStats();
      setStats(fresh);
    } catch (err) {
      setError(err.message);
    }
  };

  const refreshAssignments = async () => {
    const data = await listAssignments();
    setAssignments(data);
    setSelectedAssignment((prev) => data.find((item) => item.assignment_id === prev?.assignment_id) || data[0] || null);
  };

  const refreshScenarios = async () => {
    const data = await listScenarios();
    setScenarios(data);
  };

  const refreshAnalyses = async () => {
    const data = await listAnalyses();
    setAnalysisHistory(data);
  };

  const handleAnalyze = async ({ sentence, goals, detected }) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeSentence({ sentence, level, goals });
      setCurrentAnalysis(result);
      setAnalysisHistory((prev) => [result, ...prev.filter((item) => item.analysis_id !== result.analysis_id)].slice(0, 15));
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAssignment = async (analysis, goalsOverride) => {
    if (!analysis) return;
    setLoading(true);
    setError(null);
    try {
      const assignment = await createAssignment({
        sentence: analysis.sentence,
        level,
        goals: goalsOverride && goalsOverride.length > 0 ? goalsOverride : analysis.focus,
        analysis_id: analysis.analysis_id,
      });
      setAssignments((prev) => [assignment, ...prev.filter((item) => item.assignment_id !== assignment.assignment_id)]);
      setSelectedAssignment(assignment);
      setCurrentView(VIEWS.ASSIGNMENTS);
      await refreshStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAssignment = async (assignmentId, payload) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await updateAssignment(assignmentId, payload);
      setAssignments((prev) => prev.map((item) => (item.assignment_id === updated.assignment_id ? updated : item)));
      setSelectedAssignment(updated);
      await refreshStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateScenario = async ({ theme, recently_learned }) => {
    setLoading(true);
    setError(null);
    try {
      await createScenario({ theme, recently_learned, level });
      await refreshScenarios();
      setCurrentView(VIEWS.SCENARIOS);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const derivedStats = useMemo(() => stats, [stats]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header current={currentView} setCurrent={setCurrentView} />

      {error && (
        <div className="max-w-4xl mx-auto mt-4 px-4">
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
            <button
              className="ml-3 text-xs font-semibold underline"
              onClick={() => setError(null)}
            >
              Ausblenden
            </button>
          </div>
        </div>
      )}

      {currentView === VIEWS.DASHBOARD && (
        <Dashboard
          stats={derivedStats}
          assignments={assignments}
          scenarios={scenarios}
          analysisHistory={analysisHistory}
          onNavigate={setCurrentView}
        />
      )}

      {currentView === VIEWS.SENTENCE && (
        <SentenceLab
          level={level}
          analysis={currentAnalysis}
          history={analysisHistory}
          loading={loading}
          onAnalyze={handleAnalyze}
          onGenerateAssignment={handleGenerateAssignment}
          onSelectAnalysis={(entry) => setCurrentAnalysis(entry)}
        />
      )}

      {currentView === VIEWS.ASSIGNMENTS && (
        <AssignmentBoard
          assignments={assignments}
          selectedAssignment={selectedAssignment}
          onSelectAssignment={setSelectedAssignment}
          onUpdateAssignment={handleUpdateAssignment}
          loading={loading}
        />
      )}

      {currentView === VIEWS.SCENARIOS && (
        <ScenarioTrainer
          scenarios={scenarios}
          onGenerateScenario={handleGenerateScenario}
          loading={loading}
        />
      )}
    </div>
  );
}
