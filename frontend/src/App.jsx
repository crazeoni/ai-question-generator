import { useState } from "react";

export default function App() {
  const [text, setText] = useState("");
  const [questionCount, setQuestionCount] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [questions, setQuestions] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setQuestions("");

    try {
      const res = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          question_count: questionCount,
          difficulty,
          max_tokens: 400,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Request failed");
      }

      const data = await res.json();
      console.log("DATA FROM BACKEND:", data);
      setQuestions(data.questions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: "2rem auto", padding: 20 }}>
      <h1>AI Question Generator</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          placeholder="Paste your text or article here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          style={{ width: "100%", padding: 8 }}
        />

        <div style={{ marginTop: 8, display: "flex", gap: "1rem" }}>
          <label>
            Number of Questions:
            <input
              type="number"
              min="1"
              max="20"
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              style={{ marginLeft: 8, width: "60px" }}
            />
          </label>

          <label>
            Difficulty:
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              style={{ marginLeft: 8 }}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </label>
        </div>

        <div style={{ marginTop: 12 }}>
          <button type="submit" disabled={loading}>
            {loading ? "Generating..." : "Generate Questions"}
          </button>
        </div>
      </form>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {questions && (
        <div style={{ marginTop: 24 }}>
          <h3>Generated Questions</h3>
          <pre
            style={{
              background: "#070202ff",
              padding: "1rem",
              borderRadius: "8px",
              whiteSpace: "pre-wrap",
            }}
          >
            {questions}
          </pre>
        </div>
      )}
    </div>
  );
}
