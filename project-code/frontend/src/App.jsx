import { useEffect, useMemo, useState } from "react";
import { apiRequest, parseJwt } from "./api";

const roleLabel = {
  member: "Member",
  executive: "ULGA Executive Team",
  admin: "System Administrator",
};

function App() {
  const [token, setToken] = useState(localStorage.getItem("ulga_access_token") || "");
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem("ulga_refresh_token") || "");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [authMode, setAuthMode] = useState("login");
  const [question, setQuestion] = useState("");
  const [parentId, setParentId] = useState("");
  const [lastAnswer, setLastAnswer] = useState(null);
  const [history, setHistory] = useState([]);
  const [faq, setFaq] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [overrideThreadId, setOverrideThreadId] = useState("");
  const [overrideAnswer, setOverrideAnswer] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadVersion, setUploadVersion] = useState("v1.0");
  const [uploadTitle, setUploadTitle] = useState("ULGA By-Law Document");
  const [message, setMessage] = useState("");

  const claims = useMemo(() => parseJwt(token), [token]);
  const role = claims.role || "member";
  const isExecutive = role === "executive" || role === "admin";
  const isAdmin = role === "admin";

  useEffect(() => {
    if (token) {
      loadHistory();
      loadFaq();
      if (isAdmin) {
        loadAnalytics();
      }
    }
  }, [token]);

  async function login(event) {
    event.preventDefault();
    setMessage("");
    try {
      const data = await apiRequest("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      localStorage.setItem("ulga_access_token", data.access);
      localStorage.setItem("ulga_refresh_token", data.refresh);
      setToken(data.access);
      setRefreshToken(data.refresh);
      setMessage("Login successful.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function signup(event) {
    event.preventDefault();
    setMessage("");
    try {
      const data = await apiRequest("/auth/register/", {
        method: "POST",
        body: JSON.stringify({
          username,
          email,
          password,
          confirm_password: confirmPassword,
        }),
      });
      localStorage.setItem("ulga_access_token", data.access);
      localStorage.setItem("ulga_refresh_token", data.refresh);
      setToken(data.access);
      setRefreshToken(data.refresh);
      setMessage("Signup successful.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  function logout() {
    localStorage.removeItem("ulga_access_token");
    localStorage.removeItem("ulga_refresh_token");
    setToken("");
    setRefreshToken("");
    setHistory([]);
    setLastAnswer(null);
    setAnalytics(null);
    setMessage("Logged out.");
  }

  async function loadHistory() {
    try {
      const data = await apiRequest("/questions/history/", { method: "GET" }, token);
      setHistory(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadFaq() {
    try {
      const data = await apiRequest("/faq/", { method: "GET" }, token);
      setFaq(data);
    } catch {
      setFaq([]);
    }
  }

  async function askQuestion(event) {
    event.preventDefault();
    setMessage("");
    try {
      const payload = { question };
      if (parentId) payload.parent_id = Number(parentId);
      const data = await apiRequest("/questions/ask/", {
        method: "POST",
        body: JSON.stringify(payload),
      }, token);
      setLastAnswer(data);
      setQuestion("");
      setParentId("");
      await loadHistory();
      await loadFaq();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function submitFeedback(threadId, helpful) {
    setMessage("");
    try {
      await apiRequest("/questions/feedback/", {
        method: "POST",
        body: JSON.stringify({ thread_id: threadId, helpful, comments: "" }),
      }, token);
      setMessage("Feedback submitted.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function uploadDocument(event) {
    event.preventDefault();
    if (!uploadFile) {
      setMessage("Please choose a file first.");
      return;
    }
    const form = new FormData();
    form.append("title", uploadTitle);
    form.append("version", uploadVersion);
    form.append("file", uploadFile);
    form.append("is_active", "true");

    try {
      await apiRequest("/documents/upload/", {
        method: "POST",
        body: form,
      }, token);
      setMessage("Document uploaded and indexed.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadAnalytics() {
    try {
      const data = await apiRequest("/admin/analytics/", { method: "GET" }, token);
      setAnalytics(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function overrideAnswerSubmit(event) {
    event.preventDefault();
    try {
      await apiRequest(`/admin/override-answer/${overrideThreadId}/`, {
        method: "POST",
        body: JSON.stringify({ answer: overrideAnswer }),
      }, token);
      setMessage("Override answer saved.");
      setOverrideAnswer("");
      setOverrideThreadId("");
      await loadHistory();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function rebuildIndex() {
    try {
      const data = await apiRequest("/documents/rebuild-index/", { method: "POST" }, token);
      setMessage(`Index rebuilt: ${data.chunk_count} chunks.`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  if (!token) {
    return (
      <main className="container">
        <h1>ULGA By-Law Question Answering</h1>
        <form className="card" onSubmit={authMode === "login" ? login : signup}>
          <h2>{authMode === "login" ? "Login" : "Create Account"}</h2>
          <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          {authMode === "signup" && (
            <input placeholder="Email (optional)" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          )}
          <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {authMode === "signup" && (
            <input placeholder="Confirm Password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          )}
          <button type="submit">{authMode === "login" ? "Sign In" : "Sign Up"}</button>
          <button
            type="button"
            className="secondary"
            onClick={() => {
              setAuthMode(authMode === "login" ? "signup" : "login");
              setMessage("");
            }}
          >
            {authMode === "login" ? "Need an account? Sign up" : "Have an account? Sign in"}
          </button>
          {message && <p className="message">{message}</p>}
        </form>
      </main>
    );
  }

  return (
    <main className="container">
      <header className="header-row">
        <h1>ULGA By-Law Question Answering</h1>
        <div>
          <span className="role">Role: {roleLabel[role] || "Member"}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <form className="card" onSubmit={askQuestion}>
        <h2>Ask a Question</h2>
        <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask your by-law question..." required />
        <input value={parentId} onChange={(e) => setParentId(e.target.value)} placeholder="Optional follow-up parent question ID" />
        <button type="submit">Submit</button>
      </form>

      {lastAnswer && (
        <section className="card">
          <h2>Latest Answer</h2>
          <p>{lastAnswer.final_answer}</p>
          <h3>Sources</h3>
          <ul>
            {lastAnswer.sources?.map((source, index) => (
              <li key={index}>
                <strong>{source.source || "document"}</strong> page {source.page}: {source.text}
              </li>
            ))}
          </ul>
          <div className="button-row">
            <button onClick={() => submitFeedback(lastAnswer.id, true)}>Helpful</button>
            <button onClick={() => submitFeedback(lastAnswer.id, false)}>Not Helpful</button>
          </div>
        </section>
      )}

      <section className="card">
        <h2>Search History</h2>
        <ul>
          {history.map((item) => (
            <li key={item.id}>
              <strong>#{item.id}</strong> {item.question}
              <div>{item.final_answer}</div>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>FAQ</h2>
        <ul>
          {faq.map((item) => (
            <li key={item.id}>
              <strong>{item.question}</strong>
              <div>{item.answer}</div>
            </li>
          ))}
        </ul>
      </section>

      {isExecutive && (
        <form className="card" onSubmit={uploadDocument}>
          <h2>Upload By-Law Document</h2>
          <input value={uploadTitle} onChange={(e) => setUploadTitle(e.target.value)} placeholder="Document title" required />
          <input value={uploadVersion} onChange={(e) => setUploadVersion(e.target.value)} placeholder="Version (e.g. v1.0)" required />
          <input type="file" onChange={(e) => setUploadFile(e.target.files?.[0] || null)} accept=".pdf,.docx,.txt,.md" required />
          <button type="submit">Upload and Index</button>
        </form>
      )}

      {isAdmin && (
        <section className="card">
          <h2>Admin Panel</h2>
          <div className="button-row">
            <button onClick={loadAnalytics}>Refresh Analytics</button>
            <button onClick={rebuildIndex}>Rebuild Index</button>
          </div>
          {analytics && (
            <pre>{JSON.stringify(analytics, null, 2)}</pre>
          )}
          <form onSubmit={overrideAnswerSubmit}>
            <h3>Manual Answer Override</h3>
            <input value={overrideThreadId} onChange={(e) => setOverrideThreadId(e.target.value)} placeholder="Thread ID" required />
            <textarea value={overrideAnswer} onChange={(e) => setOverrideAnswer(e.target.value)} placeholder="Correct answer" required />
            <button type="submit">Save Override</button>
          </form>
        </section>
      )}

      {message && <p className="message">{message}</p>}
    </main>
  );
}

export default App;
