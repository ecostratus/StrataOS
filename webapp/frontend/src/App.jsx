import { useEffect, useMemo, useState } from "react";

const api = {
  async get(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`${path} failed`);
    return res.json();
  },
  async post(path, body = {}) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `${path} failed`);
    }
    return res.json();
  }
};

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [runs, setRuns] = useState([]);
  const [activity, setActivity] = useState([]);
  const [bucketColors, setBucketColors] = useState({});
  const [loadingRun, setLoadingRun] = useState(false);
  const [generationState, setGenerationState] = useState({
    kind: null,
    loading: false,
    artifact: null,
    error: null,
    promptText: "",
  });
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [status, setStatus] = useState("");
  const [showPromptText, setShowPromptText] = useState(false);
  const [setupStatusLoading, setSetupStatusLoading] = useState(true);
  const [setupRequired, setSetupRequired] = useState(false);
  const [setupSkipped, setSetupSkipped] = useState(false);
  const [setupApiKey, setSetupApiKey] = useState("");
  const [setupSaving, setSetupSaving] = useState(false);
  const [setupError, setSetupError] = useState("");

  const selectedJob = useMemo(
    () => jobs.find((job) => job.id === selectedJobId) || null,
    [jobs, selectedJobId]
  );

  const loadAll = async () => {
    const [jobsData, runsData, activityData, scoring] = await Promise.all([
      api.get("/api/jobs?limit=120"),
      api.get("/api/runs?limit=25"),
      api.get("/api/activity?limit=80"),
      api.get("/api/metadata/scoring")
    ]);
    setJobs(jobsData);
    setRuns(runsData);
    setActivity(activityData);
    setBucketColors(scoring.bucketColors || {});
    if (!selectedJobId && jobsData.length) setSelectedJobId(jobsData[0].id);
  };

  useEffect(() => {
    let mounted = true;

    const checkSetupStatus = async () => {
      try {
        const setup = await api.get("/api/setup/status");
        if (!mounted) return;
        setSetupRequired(!setup.configured);
      } catch (err) {
        if (!mounted) return;
        setSetupRequired(true);
        setSetupError("We couldn't verify setup right now. You can skip for now and continue.");
      } finally {
        if (mounted) setSetupStatusLoading(false);
      }
    };

    checkSetupStatus();
    loadAll().catch((err) => setStatus(String(err)));
    const timer = setInterval(() => {
      api.get("/api/activity?limit=80").then(setActivity).catch(() => {});
    }, 6000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  const runDiscovery = async () => {
    setLoadingRun(true);
    setStatus("Running job discovery...");
    try {
      const result = await api.post("/api/runs/job-discovery");
      setStatus(`Run #${result.run_id} completed, mirrored ${result.mirrored_jobs} jobs`);
      await loadAll();
    } catch (err) {
      setStatus(`Discovery failed: ${String(err)}`);
    } finally {
      setLoadingRun(false);
    }
  };

  const generatePrompt = async (kind) => {
    if (!selectedJobId) return;
    const label = kind === "resume" ? "resume" : "outreach message";
    setGenerationState({
      kind,
      loading: true,
      artifact: null,
      error: null,
      promptText: "",
    });
    setShowPromptText(false);
    setStatus(`Generating your ${label}...`);
    try {
      const result = await api.post(`/api/prompts/${kind}`, { job_id: selectedJobId, no_sources: true });
      if (result.status === "error") {
        const errorMessage = result.error?.message || "The content could not be generated right now. Please try again.";
        const errorCode = result.error?.code || "generation_failed";
        console.error("Generation failed", { kind, errorCode });
        setGenerationState({
          kind,
          loading: false,
          artifact: null,
          error: { message: errorMessage, code: errorCode },
          promptText: result.prompt_text || "",
        });
        setStatus(errorMessage);
        return;
      }

      setGenerationState({
        kind,
        loading: false,
        artifact: result.artifact || null,
        error: null,
        promptText: result.prompt_text || "",
      });
      setStatus(`${kind === "resume" ? "Resume" : "Outreach message"} ready`);
      await loadAll();
    } catch (err) {
      const message = `Could not generate your ${label} right now. Please try again.`;
      setGenerationState({
        kind,
        loading: false,
        artifact: null,
        error: { message, code: "network_error" },
        promptText: "",
      });
      setStatus(message);
    }
  };

  const clearGeneration = () => {
    setGenerationState({
      kind: null,
      loading: false,
      artifact: null,
      error: null,
      promptText: "",
    });
    setShowPromptText(false);
    setStatus("");
  };

  const saveSetupKey = async () => {
    const trimmed = setupApiKey.trim();
    if (!trimmed) {
      setSetupError("Please paste your OpenAI API key before saving.");
      return;
    }

    setSetupApiKey("");
    setSetupSaving(true);
    setSetupError("");
    try {
      await api.post("/api/setup/openai-key", { api_key: trimmed });
      const refreshed = await api.get("/api/setup/status");
      if (!refreshed.configured) {
        setSetupError("Setup did not complete. Please try again.");
        return;
      }
      setSetupRequired(false);
      setSetupSkipped(false);
      setStatus("Setup complete. You can now generate resumes and outreach messages.");
    } catch (err) {
      setSetupError("We couldn't save your key right now. Please try again.");
    } finally {
      setSetupSaving(false);
    }
  };

  const skipSetupForNow = () => {
    setSetupRequired(false);
    setSetupSkipped(true);
    setSetupError("");
    setStatus("Setup skipped. Job discovery and browsing still work.");
  };

  const generationPanelTitle = generationState.kind === "outreach" ? "Your Outreach Message" : "Your Resume";
  const generationEmptyText = generationState.kind === "outreach"
    ? "Select a job, then click Create Outreach Message."
    : "Select a job, then click Create Resume.";
  const hasArtifact = Boolean(generationState.artifact?.content);

  const bucketBadge = (bucket) => ({
    backgroundColor: (bucket && bucketColors[bucket]) || "#cbd5e1",
    color: "#0b1726"
  });

  if (setupStatusLoading) {
    return (
      <div className="min-h-screen p-4 md:p-8">
        <div className="mx-auto max-w-3xl">
          <section className="card p-6">
            <h1 className="text-2xl font-bold">StrataOS Control Center</h1>
            <p className="mt-3 text-sm text-slate-600">Checking your setup...</p>
          </section>
        </div>
      </div>
    );
  }

  if (setupRequired) {
    return (
      <div className="min-h-screen p-4 md:p-8">
        <div className="mx-auto max-w-3xl space-y-4">
          <section className="card p-6">
            <h1 className="text-2xl font-bold">Let's get you set up</h1>
            <p className="mt-3 text-sm text-slate-700">
              To create finished resumes and outreach messages, StrataOS needs an OpenAI API key.
              Job discovery still works without one.
            </p>

            <label className="mt-4 block text-sm font-semibold text-slate-800" htmlFor="openai-api-key">
              OpenAI API key
            </label>
            <input
              id="openai-api-key"
              type="password"
              value={setupApiKey}
              onChange={(event) => setSetupApiKey(event.target.value)}
              placeholder="Paste your OpenAI API key"
              autoComplete="off"
              className="mt-2 w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900"
            />

            {setupError ? (
              <p className="mt-3 rounded border border-rose-200 bg-rose-50 p-2 text-sm text-rose-900">{setupError}</p>
            ) : null}

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={saveSetupKey}
                disabled={setupSaving}
                className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
              >
                {setupSaving ? "Saving..." : "Save and Continue"}
              </button>
              <button
                type="button"
                onClick={skipSetupForNow}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Skip for now
              </button>
            </div>
          </section>

          {setupSkipped ? (
            <section className="card p-4 text-sm text-slate-600">
              You can still find jobs now and add your API key later.
            </section>
          ) : null}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-4">
        <header className="card p-4 md:p-6">
          <h1 className="text-2xl font-bold">StrataOS Control Center</h1>
          <p className="mt-1 text-sm text-slate-600">
            Find jobs, create a tailored resume or outreach message, and keep the AI prompt available as an advanced reference.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={runDiscovery}
              disabled={loadingRun}
              className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
            >
              {loadingRun ? "Finding jobs..." : "Find Jobs"}
            </button>
            <button
              onClick={() => generatePrompt("resume")}
              disabled={!selectedJobId || generationState.loading}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-400 disabled:opacity-60"
            >
              {generationState.loading && generationState.kind === "resume" ? "Creating your resume..." : "Create Resume"}
            </button>
            <button
              onClick={() => generatePrompt("outreach")}
              disabled={!selectedJobId || generationState.loading}
              className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500 disabled:opacity-60"
            >
              {generationState.loading && generationState.kind === "outreach" ? "Creating your outreach message..." : "Create Outreach Message"}
            </button>
          </div>
          <p className="mt-3 text-sm text-slate-700">{status || "Pick a job, then create a resume or outreach message."}</p>

          <div className="mt-4 rounded border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            <div className="font-semibold text-slate-900">How this works</div>
            <ol className="mt-2 space-y-1 pl-5 list-decimal">
              <li>Find a job and click a row to select it.</li>
              <li>Choose Create Resume or Create Outreach Message.</li>
              <li>Read the result here, and open the advanced prompt only if you need it.</li>
            </ol>
          </div>
        </header>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="card overflow-hidden lg:col-span-2">
            <div className="border-b border-slate-200 px-4 py-3 font-semibold">Jobs and Runs</div>
            <div className="max-h-[380px] overflow-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-3 py-2">Run</th>
                    <th className="px-3 py-2">Company</th>
                    <th className="px-3 py-2">Role</th>
                    <th className="px-3 py-2">Score</th>
                    <th className="px-3 py-2">Bucket</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr
                      key={job.id}
                      onClick={() => setSelectedJobId(job.id)}
                      className={`cursor-pointer border-t border-slate-100 ${job.id === selectedJobId ? "bg-teal-50" : "hover:bg-slate-50"}`}
                    >
                      <td className="px-3 py-2 text-slate-500">#{job.run_id}</td>
                      <td className="px-3 py-2">{job.company || "-"}</td>
                      <td className="px-3 py-2">{job.title || "-"}</td>
                      <td className="px-3 py-2">{job.score != null ? Number(job.score).toFixed(2) : "-"}</td>
                      <td className="px-3 py-2">
                        <span className="rounded px-2 py-1 text-xs font-semibold" style={bucketBadge(job.bucket)}>
                          {job.bucket || "-"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card p-4">
            <h2 className="text-base font-semibold">Selected Job</h2>
            {!selectedJob ? (
              <p className="mt-3 text-sm text-slate-500">Pick a job from the list to see the details here.</p>
            ) : (
              <div className="mt-3 space-y-2 text-sm">
                <p><span className="font-semibold">Company:</span> {selectedJob.company || "-"}</p>
                <p><span className="font-semibold">Role:</span> {selectedJob.title || "-"}</p>
                <p><span className="font-semibold">Location:</span> {selectedJob.location || "-"}</p>
                <p><span className="font-semibold">Source:</span> {selectedJob.source || "-"}</p>
                <a className="break-all text-sky-700 underline" href={selectedJob.url || "#"} target="_blank" rel="noreferrer">
                  {selectedJob.url || "No URL"}
                </a>
              </div>
            )}
            <div className="mt-4 border-t border-slate-100 pt-3">
              <h3 className="text-sm font-semibold">Recent Runs</h3>
              <ul className="mt-2 space-y-1 text-xs text-slate-600">
                {runs.slice(0, 8).map((run) => (
                  <li key={run.id}>#{run.id} {run.run_type} - {run.status}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="card p-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold">{generationPanelTitle}</h2>
              {hasArtifact && (
                <button
                  onClick={clearGeneration}
                  className="text-xs font-semibold text-slate-600 underline hover:text-slate-900"
                >
                  Clear
                </button>
              )}
            </div>

            {!generationState.kind && !generationState.loading && !generationState.error && !hasArtifact ? (
              <p className="mt-3 text-sm text-slate-500">{generationEmptyText}</p>
            ) : null}

            {generationState.loading ? (
              <div className="mt-3 rounded border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                <div className="font-semibold text-slate-800">Creating it now...</div>
                <p className="mt-1">The app is preparing your {generationState.kind === "outreach" ? "outreach message" : "resume"}.</p>
              </div>
            ) : null}

            {generationState.error ? (
              <div className="mt-3 rounded border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
                <div className="font-semibold">Could not generate content</div>
                <p className="mt-1">{generationState.error.message}</p>
              </div>
            ) : null}

            {hasArtifact ? (
              <div className="mt-3 space-y-3">
                <pre className="max-h-80 overflow-auto whitespace-pre-wrap rounded bg-slate-900 p-3 text-xs text-slate-100">
                  {generationState.artifact.content}
                </pre>

                <div className="rounded border border-slate-200 bg-slate-50 p-3 text-sm">
                  <button
                    onClick={() => setShowPromptText((current) => !current)}
                    className="font-semibold text-slate-800 underline hover:text-slate-950"
                  >
                    {showPromptText ? "Hide the AI prompt (advanced)" : "Show the AI prompt (advanced)"}
                  </button>
                  {showPromptText ? (
                    <pre className="mt-3 max-h-56 overflow-auto whitespace-pre-wrap rounded bg-slate-900 p-3 text-xs text-slate-100">
                      {generationState.promptText || "No prompt text available."}
                    </pre>
                  ) : null}
                </div>
              </div>
            ) : null}
          </div>
          <div className="card p-4">
            <h2 className="text-base font-semibold">Recent Activity</h2>
            <div className="mt-3 max-h-80 space-y-2 overflow-auto text-xs">
              {activity.length === 0 && <p className="text-slate-500">No activity yet.</p>}
              {activity.slice().reverse().map((event, index) => (
                <div key={index} className="rounded border border-slate-200 bg-slate-50 p-2">
                  <div className="font-semibold text-slate-700">{event.category || "event"}</div>
                  <div className="text-slate-500">{event.ts || ""}</div>
                  <div className="text-slate-700">{event.event || ""}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
