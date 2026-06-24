CREATE TABLE package_runs (
  run_id TEXT NOT NULL,
  package_id TEXT NOT NULL,
  worker TEXT NOT NULL,
  status TEXT NOT NULL CHECK (
    status IN ('queued', 'started', 'done', 'error')
  ),
  updated_at TEXT NOT NULL,
  PRIMARY KEY (run_id, package_id)
);

CREATE TABLE package_events (
  run_id TEXT NOT NULL,
  package_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
