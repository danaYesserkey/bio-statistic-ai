import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

const DEFAULT_PROFILE = {
  full_name: "Студент",
  email: "",
  group: "",
  specialty: "",
  student_id: "",
  university: "ҚазҰМУ",
  role: "STUDENT",
};

const MODULES = [
  {
    id: "data_types",
    title: "1-модуль: Деректер түрлері",
    description: "",
  },
];

function loadJSON(key, fallback) {
  try {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : fallback;
  } catch {
    return fallback;
  }
}

function nowTime() {
  return new Date().toLocaleTimeString("kk-KZ", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getInitials(name) {
  return (
    (name || "ST")
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("") || "ST"
  );
}

function App() {
  const [page, setPage] = useState(() =>
    localStorage.getItem("access") || localStorage.getItem("registeredLocal")
      ? "home"
      : "login"
  );

  const [profile, setProfile] = useState(() =>
    loadJSON("studentProfile", DEFAULT_PROFILE)
  );

  const [courseProgress, setCourseProgress] = useState(() =>
    loadJSON("courseProgress", {})
  );

  const [auth, setAuth] = useState(() => ({
    access: localStorage.getItem("access") || "",
    refresh: localStorage.getItem("refresh") || "",
  }));

  const [openedModules, setOpenedModules] = useState({ data_types: true });
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Сәлеметсіз бе! Биостатистика бойынша сұрағыңызды жазыңыз. Мен материалдарға сүйеніп, түсінікті жауап беремін.",
      time: "09:00",
    },
  ]);
  const [input, setInput] = useState("");
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const isLoggedIn = Boolean(auth.access || localStorage.getItem("registeredLocal"));

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const saveProfile = (nextProfile) => {
    setProfile(nextProfile);
    localStorage.setItem("studentProfile", JSON.stringify(nextProfile));
  };

  const saveCourseProgress = (nextProgress) => {
    setCourseProgress(nextProgress);
    localStorage.setItem("courseProgress", JSON.stringify(nextProgress));
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("registeredLocal");
    setAuth({ access: "", refresh: "" });
    setPage("login");
  };

  const sendMessage = async () => {
    const text = input.trim();
    if ((!text && attachedFiles.length === 0) || loading) return;

    const fileSummary = attachedFiles.length
      ? "\n\nТіркелген файлдар: " +
        attachedFiles
          .map((file) => `${file.name} (${file.type || "unknown"})`)
          .join(", ")
      : "";

    const userMessage = {
      role: "user",
      content: text || "Файл тіркелді.",
      apiContent: (text || "Студент файл тіркеді.") + fileSummary,
      files: attachedFiles,
      time: nowTime(),
    };

    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setAttachedFiles([]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: nextMessages.map((msg) => ({
            role: msg.role,
            content: msg.apiContent || msg.content,
          })),
        }),
      });

      const data = await response.json().catch(() => ({}));
      const assistantText =
        data.answer ||
        data.details ||
        data.error ||
        "AI жауап бере алмады. Backend немесе API лимитін тексеріңіз.";

      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: assistantText,
          time: nowTime(),
        },
      ]);
    } catch (error) {
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content:
            "Backend-ке қосылу қатесі. Django сервері қосулы ма тексеріңіз: " +
            error.message,
          time: nowTime(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files || []).map((file) => ({
      name: file.name,
      type: file.type,
      size: file.size,
    }));

    if (files.length > 0) {
      setAttachedFiles((prev) => [...prev, ...files]);
      setPage("practice");
    }

    event.target.value = "";
  };

  const quickAsk = (text) => {
    setInput(text);
    setPage("practice");
  };

  if (page === "login") {
    return <LoginPage setPage={setPage} setAuth={setAuth} saveProfile={saveProfile} />;
  }

  if (page === "register") {
    return (
      <RegisterPage setPage={setPage} setAuth={setAuth} saveProfile={saveProfile} />
    );
  }

  return (
    <div className="app-shell">
      <TopNav page={page} setPage={setPage} logout={logout} isLoggedIn={isLoggedIn} />

      <input
        ref={fileInputRef}
        type="file"
        className="hidden-file-input"
        multiple
        accept=".csv,.xlsx,.xls,.pdf,.doc,.docx,.ppt,.pptx,image/*"
        onChange={handleFileSelect}
      />

      <main className="app-main">
        {page === "home" && (
          <HomePage profile={profile} setPage={setPage} quickAsk={quickAsk} />
        )}

        {page === "course" && (
          <CoursePage
            modules={MODULES}
            openedModules={openedModules}
            courseProgress={courseProgress}
            saveCourseProgress={saveCourseProgress}
            toggleModule={(id) =>
              setOpenedModules((prev) => ({ ...prev, [id]: !prev[id] }))
            }
          />
        )}

        {page === "practice" && (
          <PracticePage
            profile={profile}
            messages={messages}
            input={input}
            setInput={setInput}
            loading={loading}
            attachedFiles={attachedFiles}
            removeFile={(name) =>
              setAttachedFiles((prev) => prev.filter((file) => file.name !== name))
            }
            sendMessage={sendMessage}
            handleKeyDown={handleKeyDown}
            openFilePicker={() => fileInputRef.current?.click()}
            quickAsk={quickAsk}
            chatEndRef={chatEndRef}
          />
        )}

        {page === "profile" && (
          <ProfilePage
            profile={profile}
            setPage={setPage}
            modules={MODULES}
            courseProgress={courseProgress}
          />
        )}
      </main>
    </div>
  );
}

function TopNav({ page, setPage, logout }) {
  const links = [
    ["home", "Басты бет"],
    ["course", "Курс"],
    ["practice", "AI чат"],
    ["profile", "Профиль"],
  ];

  return (
    <header className="top-nav">
      <button className="brand" onClick={() => setPage("home")} type="button">
        <strong>BioStat</strong>
        <span>ҚазҰМУ</span>
      </button>

      <nav className="nav-links">
        {links.map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setPage(key)}
            className={page === key ? "active" : ""}
          >
            {label}
          </button>
        ))}
      </nav>

      <button className="logout-button" type="button" onClick={logout}>
        Шығу
      </button>
    </header>
  );
}

function HomePage({ profile, setPage, quickAsk }) {
  const currentModule = MODULES[0];

  return (
    <section className="home-page">
      <div className="page-heading home-heading">
        <p className="page-kicker">BioStat · ҚазҰМУ</p>
        <h1>Қош келдіңіз, {profile.full_name || "студент"}!</h1>
        <p className="page-subtitle">Биостатистиканы өз қарқыныңызбен үйреніңіз</p>
      </div>

      <div className="home-three-grid">
        <article className="home-action-card">
          <p className="card-label">Курс</p>
          <h2>{currentModule.title}</h2>
          <p className="card-note">Қазіргі модуль</p>
          <button type="button" onClick={() => setPage("course")}>
            Модульді ашу
          </button>
        </article>

        <article className="home-action-card home-action-card-gold">
          <p className="card-label">AI көмекші</p>
          <h2>Сұрағыңызды қойыңыз</h2>
          <div className="quick-action-list">
            <button type="button" onClick={() => quickAsk("Деректер түрлері деген не?")}>
              Деректер түрлері
            </button>
            <button type="button" onClick={() => quickAsk("Қан тобы қандай дерек түріне жатады?")}>
              Қан тобы
            </button>
          </div>
          <button className="gold-action" type="button" onClick={() => setPage("practice")}>
            AI чатты ашу
          </button>
        </article>

        <article className="home-action-card">
          <p className="card-label">Профиль</p>
          <h2>Оқу прогресі</h2>
          <p className="card-note">Нәтижелер мен жеке деректер</p>
          <button type="button" onClick={() => setPage("profile")}>
            Профильді қарау
          </button>
        </article>
      </div>
    </section>
  );
}


function getModuleStats(module, courseProgress) {
  const progress = courseProgress[module.id] || {};
  const lessons = module.lessons || [];
  const completedLessons = progress.lessonsCompleted || [];
  const testExists = Boolean(module.test);
  const totalItems = lessons.length + (testExists ? 1 : 0);

  if (totalItems === 0) {
    return {
      percent: 0,
      completed: false,
      completedItems: 0,
      totalItems: 0,
      label: "Материалдар әлі қосылмаған",
    };
  }

  const doneItems =
    lessons.filter((lesson) => completedLessons.includes(lesson.id)).length +
    (progress.testPassed ? 1 : 0);

  return {
    percent: Math.round((doneItems / totalItems) * 100),
    completed: doneItems === totalItems,
    completedItems: doneItems,
    totalItems,
    label: `${doneItems}/${totalItems} бөлім аяқталды`,
  };
}

function getCourseStats(modules, courseProgress) {
  const moduleStats = modules.map((module) => getModuleStats(module, courseProgress));
  const completedModules = moduleStats.filter((item) => item.completed).length;
  const totalPercent = modules.length
    ? Math.round(moduleStats.reduce((sum, item) => sum + item.percent, 0) / modules.length)
    : 0;

  // Quiz results will be saved later as courseProgress[moduleId].quizScores = [80, 90, ...].
  // Until then the UI honestly shows that no score has been calculated yet.
  const quizScores = modules.flatMap((module) => {
    const scores = courseProgress[module.id]?.quizScores;
    return Array.isArray(scores) ? scores.filter((score) => Number.isFinite(Number(score))) : [];
  });

  const averageScore = quizScores.length
    ? Math.round(quizScores.reduce((sum, score) => sum + Number(score), 0) / quizScores.length)
    : null;

  return {
    completedModules,
    totalModules: modules.length,
    totalPercent,
    moduleStats,
    averageScore,
    quizCount: quizScores.length,
  };
}

function CoursePage({ modules, openedModules, toggleModule, courseProgress }) {
  return (
    <section className="page-shell course-page-shell">
      <div className="page-heading">
        <p className="page-kicker">Курс</p>
        <h1>Курс материалдары</h1>
      </div>

      <div className="course-layout">
        {modules.map((module) => {
          const stats = getModuleStats(module, courseProgress);
          return (
            <article className="course-module" key={module.id}>
              <button
                className="course-module-head"
                type="button"
                onClick={() => toggleModule(module.id)}
              >
                <div>
                  <span className="course-chevron">{openedModules[module.id] ? "⌄" : "›"}</span>
                  <h2>{module.title}</h2>
                </div>
                <strong>{stats.percent}%</strong>
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}


function PracticePage({
  profile,
  messages,
  input,
  setInput,
  loading,
  attachedFiles,
  removeFile,
  sendMessage,
  handleKeyDown,
  openFilePicker,
  quickAsk,
  chatEndRef,
}) {
  const studentInitials = getInitials(profile.full_name || "Студент");

  return (
    <section className="chat-page">
      <aside className="chat-sidebar">
        <span className="sidebar-label">AI MODE</span>
        <h2>AI көмекші</h2>
        <p>
          Сұрағыңызды жазыңыз. AI биостатистика материалдарына сүйеніп жауап
          береді.
        </p>

        <button type="button" onClick={() => quickAsk("Деректер түрлері деген не?")}>
          Деректер түрлері
        </button>
        <button
          type="button"
          onClick={() => quickAsk("Қан тобы қандай дерек түріне жатады?")}
        >
          Мысал сұрақ
        </button>
        <button type="button" onClick={openFilePicker}>
          Файл тіркеу
        </button>
      </aside>

      <section className="chat-workspace">
        <header className="chat-header">
          <div>
            <h1>AI чат</h1>
            <p>Биостатистика бойынша нақты әрі түсінікті жауап береді.</p>
          </div>
        </header>

        <div className="chat-stream">
          {messages.map((msg, index) => (
            <ChatMessage key={`${msg.time}-${index}`} msg={msg} initials={studentInitials} />
          ))}

          {loading && (
            <div className="message assistant">
              <div className="bot-avatar">AI</div>
              <div className="message-bubble">
                <p>Жауап дайындалып жатыр...</p>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <footer className="chat-composer">
          {attachedFiles.length > 0 && (
            <div className="attached-files">
              {attachedFiles.map((file) => (
                <span key={`${file.name}-${file.size}`}>
                  📎 {file.name}
                  <button type="button" onClick={() => removeFile(file.name)}>
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}

          <div className="composer-row">
            <button
              type="button"
              className="attach-button"
              onClick={openFilePicker}
              title="Файл тіркеу"
            >
              +
            </button>

            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Сұрағыңызды жазыңыз..."
              rows={1}
            />

            <button
              type="button"
              className="send-button"
              onClick={sendMessage}
              disabled={(!input.trim() && attachedFiles.length === 0) || loading}
            >
              Жіберу
            </button>
          </div>
        </footer>
      </section>
    </section>
  );
}

function ChatMessage({ msg, initials }) {
  const isUser = msg.role === "user";

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      {!isUser && <div className="bot-avatar">AI</div>}

      <div className="message-bubble">
        <p>{msg.content}</p>
        {msg.files?.length > 0 && (
          <div className="message-files">
            {msg.files.map((file) => (
              <span key={`${file.name}-${file.size}`}>📎 {file.name}</span>
            ))}
          </div>
        )}
        <small>{msg.time}</small>
      </div>

      {isUser && <div className="user-avatar">{initials || "ST"}</div>}
    </div>
  );
}

function ProfilePage({ profile, setPage, modules, courseProgress }) {
  const rows = [
    ["ФИО", profile.full_name],
    ["Email", profile.email],
    ["Топ", profile.group],
    ["Мамандық", profile.specialty],
    ["Student ID", profile.student_id],
    ["Университет", profile.university],
  ];

  const stats = getCourseStats(modules, courseProgress);
  const scoreText = stats.averageScore === null ? "—" : `${stats.averageScore}%`;

  return (
    <section className="page-shell profile-page-shell">
      <div className="page-heading">
        <p className="page-kicker">Профиль</p>
        <h1>Профиль және оқу прогресі</h1>
      </div>

      <article className="profile-card profile-card-wide">
        <div className="profile-avatar">{getInitials(profile.full_name)}</div>
        <div className="profile-main">
          <div className="profile-name-row">
            <div>
              <h2>{profile.full_name || "Студент"}</h2>
              <p>{profile.email || "—"}</p>
            </div>
            <button type="button" onClick={() => setPage("course")}>Курсқа өту</button>
          </div>

          <div className="profile-table">
            {rows.map(([label, value]) => (
              <div key={label}>
                <span>{label}</span>
                <strong>{value || "—"}</strong>
              </div>
            ))}
          </div>
        </div>
      </article>

      <div className="profile-stats-row">
        <aside className="progress-summary-card">
          <span>Оқу прогресі</span>
          <strong>{stats.totalPercent}%</strong>
          <p>{stats.completedModules}/{stats.totalModules} модуль</p>
          <div className="summary-bar"><i style={{ width: `${stats.totalPercent}%` }} /></div>
        </aside>

        <aside className="average-score-card">
          <span>Орташа балл</span>
          <strong>{scoreText}</strong>
          <p>{stats.quizCount ? `${stats.quizCount} quiz` : "Quiz нәтижесі жоқ"}</p>
        </aside>
      </div>

      <article className="course-progress-card">
        <h2>Модульдер бойынша прогресс</h2>
        {modules.map((module) => {
          const moduleStats = getModuleStats(module, courseProgress);
          return (
            <div className="progress-line" key={module.id}>
              <b>{module.title}</b>
              <div className="line-bar"><i style={{ width: `${moduleStats.percent}%` }} /></div>
              <strong>{moduleStats.percent}%</strong>
            </div>
          );
        })}
      </article>
    </section>
  );
}


function LoginPage({ setPage, setAuth, saveProfile }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const canSubmit = useMemo(() => form.email.trim() && form.password.trim(), [form]);

  const login = async () => {
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/users/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || data.error || "Login қатесі");

      localStorage.setItem("access", data.access || "local-access");
      localStorage.setItem("refresh", data.refresh || "local-refresh");
      setAuth({
        access: data.access || "local-access",
        refresh: data.refresh || "local-refresh",
      });

      const savedProfile = loadJSON("studentProfile", DEFAULT_PROFILE);
      if (data.full_name || data.email) saveProfile({ ...savedProfile, ...data });
      setPage("home");
    } catch (errorObject) {
      const savedProfile = loadJSON("studentProfile", null);
      if (savedProfile && savedProfile.email === form.email) {
        localStorage.setItem("registeredLocal", "true");
        localStorage.setItem("access", "local-access");
        localStorage.setItem("refresh", "local-refresh");
        setAuth({ access: "local-access", refresh: "local-refresh" });
        setPage("home");
        return;
      }
      setError(errorObject.message);
    }
  };

  return (
    <AuthScreen title="Жүйеге кіру" subtitle="Тіркелген email және құпиясөзді енгізіңіз">
      <input
        placeholder="Email"
        value={form.email}
        onChange={(event) => setForm({ ...form, email: event.target.value })}
      />
      <input
        placeholder="Құпиясөз"
        type="password"
        value={form.password}
        onChange={(event) => setForm({ ...form, password: event.target.value })}
      />
      <button type="button" onClick={login} disabled={!canSubmit}>
        Кіру
      </button>
      <button className="link-button" type="button" onClick={() => setPage("register")}>
        Тіркелу
      </button>
      {error && <p className="form-error">{error}</p>}
    </AuthScreen>
  );
}

function RegisterPage({ setPage, setAuth, saveProfile }) {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    group: "",
    specialty: "",
    student_id: "",
    university: "ҚазҰМУ",
    role: "STUDENT",
    password: "",
  });

  const canSubmit = useMemo(
    () =>
      form.full_name.trim() &&
      form.email.trim() &&
      form.group.trim() &&
      form.specialty.trim() &&
      form.student_id.trim() &&
      form.password.trim(),
    [form]
  );

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const register = () => {
    saveProfile({ ...DEFAULT_PROFILE, ...form });
    localStorage.setItem("registeredLocal", "true");
    localStorage.setItem("access", "local-access");
    localStorage.setItem("refresh", "local-refresh");
    setAuth({ access: "local-access", refresh: "local-refresh" });
    setPage("home");
  };

  return (
    <AuthScreen title="Тіркелу" subtitle="Студент деректерін толық енгізіңіз">
      <input
        placeholder="ФИО"
        value={form.full_name}
        onChange={(event) => update("full_name", event.target.value)}
      />
      <input
        placeholder="Email"
        value={form.email}
        onChange={(event) => update("email", event.target.value)}
      />
      <input
        placeholder="Группа"
        value={form.group}
        onChange={(event) => update("group", event.target.value)}
      />
      <input
        placeholder="Специальность"
        value={form.specialty}
        onChange={(event) => update("specialty", event.target.value)}
      />
      <input
        placeholder="Student ID"
        value={form.student_id}
        onChange={(event) => update("student_id", event.target.value)}
      />
      <input
        placeholder="Университет"
        value={form.university}
        onChange={(event) => update("university", event.target.value)}
      />
      <input
        placeholder="Құпиясөз"
        type="password"
        value={form.password}
        onChange={(event) => update("password", event.target.value)}
      />
      <button type="button" onClick={register} disabled={!canSubmit}>
        Тіркелу және кіру
      </button>
      <button className="link-button" type="button" onClick={() => setPage("login")}>
        Login бетіне өту
      </button>
    </AuthScreen>
  );
}

function AuthScreen({ title, subtitle, children }) {
  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-brand">
          <strong>BioStat</strong>
          <span>ҚазҰМУ</span>
        </div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <div className="auth-form">{children}</div>
      </div>
    </div>
  );
}

export default App;
