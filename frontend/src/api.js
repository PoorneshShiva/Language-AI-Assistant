const BASE_URL = "http://localhost:8000/v1";

async function fetchApi(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  const result = await response.json();
  if (!result.ok) {
    throw new Error(`API error: ${result.error.message}`);
  }
  return result.data;
}

export const getHealth = () => fetchApi("/health");
export const detectWords = (sentence, level, exclude_keys) => fetchApi("/words/detect", {
  method: "POST",
  body: JSON.stringify({ sentence, level, exclude_keys }),
});
export const getRandomWord = (level, exclude_keys, preferred_types) => fetchApi("/words/random", {
    method: "POST",
    body: JSON.stringify({ level, exclude_keys, preferred_types }),
});
export const getWords = (types, limit, cursor) => fetchApi(`/words?types=${types}&limit=${limit}&cursor=${cursor || ''}`);
export const getVerb = (infinitive) => fetchApi(`/verbs/${infinitive}`);
export const getNoun = (noun) => fetchApi(`/nouns/${noun}`);
export const getPrompts = (item_type, item_id, level, count) => fetchApi(`/prompts?item_type=${item_type}&item_id=${item_id}&level=${level}&count=${count}`);
export const evaluate = (item, prompt_id, expected, answer, level) => fetchApi("/evaluate", {
    method: "POST",
    body: JSON.stringify({ item, prompt_id, expected, answer, level }),
});
export const getPracticeQueue = (level, limit) => fetchApi(`/practice/queue?level=${level}&limit=${limit}`);
export const postConfidence = (item, confidence, level, telemetry) => fetchApi("/practice/confidence", {
    method: "POST",
    body: JSON.stringify({ item, confidence, level, telemetry }),
});
export const postComplete = (item) => fetchApi("/practice/complete", {
    method: "POST",
    body: JSON.stringify({ item }),
});
export const postReviewAgain = (item) => fetchApi("/practice/review-again", {
    method: "POST",
    body: JSON.stringify({ item }),
});
export const getCompleted = () => fetchApi("/completed");
export const postIgnore = (item) => fetchApi("/ignore", {
    method: "POST",
    body: JSON.stringify({ item }),
});
export const deleteIgnore = (item) => fetchApi("/ignore", {
    method: "DELETE",
    body: JSON.stringify({ item }),
});
export const getHints = (scope, cases, limit) => fetchApi(`/hints/nouns?scope=${scope}&cases=${cases}&limit=${limit}`);
export const getSettings = () => fetchApi("/settings");
export const patchSettings = (settings) => fetchApi("/settings", {
    method: "PATCH",
    body: JSON.stringify(settings),
});
export const getStats = () => fetchApi("/stats");
