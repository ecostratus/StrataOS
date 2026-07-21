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
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [promptText, setPromptText] = useState("");
  const [status, setStatus] = useState("");

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
    loadAll().catch((err) => setStatus(String(err)));
    const timer = setInterval(() => {
      api.get("/api/activity?limit=80").then(setActivity).catch(() => {});
    }, 6000);
    return () => clearInterval(timer);
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
    setStatus(`Generating ${kind} prompt...`);
    try {
      const result = await api.post(`/api/prompts/${kind}`, { job_id: selectedJobId, no_sources: true });
      setPromptText(result.prompt_text || "");
      setStatus(`${kind} prompt generated`);
      await loadAll();
    } catch (err) {
      setStatus(`Prompt generation failed: ${String(err)}`);
    }
  };

  const bucketBadge = (bucket) => ({
    backgroundColor: (bucket && bucketColors[bucket]) || "#cbd5e1",
    color: "#0b1726"
  });

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-4">
        <header className="card p-4 md:p-6">
          <h1 className="text-2xl font-bold">StrataOS Control Center</h1>
          <p className="mt-1 text-sm text-slate-600">
            One-click orchestration for job discovery, per-job prompt generation, and activity visibility.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={runDiscovery}
              disabled={loadingRun}
              className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
            >
              {loadingRun ? "Running..." : "Run Job Discovery"}
            </button>
            <button
              onClick={() => generatePrompt("resume")}
              disabled={!selectedJobId}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-400 disabled:opacity-60"
            >
              Generate Resume Prompt
            </button>
            <button
              onClick={() => generatePrompt("outreach")}
              disabled={!selectedJobId}
              className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500 disabled:opacity-60"
            >
              Generate Outreach Prompt
            </button>
          </div>
          <p className="mt-3 text-sm text-slate-700">{status}</p>
        </header>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="card overflow-hidden lg:col-span-2">
            <div className="border-b border-slate-200 px-4 py-3 font-semibold">Run Ledger and Jobs</div>
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
              <p className="mt-3 text-sm text-slate-500">No job selected.</p>
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
            <h2 className="text-base font-semibold">Generated Prompt</h2>
            <pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap rounded bg-slate-900 p-3 text-xs text-slate-100">
              {promptText || "No prompt generated yet."}
            </pre>
          </div>
          <div className="card p-4">
            <h2 className="text-base font-semibold">Activity Log</h2>
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
