// Permission log: an observe-only OpenCode plugin from the agent kit.
// It appends one JSON line per permission request and reply to
// .agent-kit/logs/permissions/YYYY-MM-DD.jsonl in the project folder.
// Record format, limits and what is never logged: procedures/permission-log.md.
// It only listens: it never answers a prompt or changes a decision, and it writes
// nothing except that log file. Secrets are removed from `pattern` with the lines of
// <KIT_DIR>/scripts/secret-patterns.txt (KIT_DIR is read from agent-kit.conf).
import fs from "node:fs"
import path from "node:path"

const CAP = 1048576 // bytes per daily file
const MAX_PATTERN = 200 // characters, after redaction
const NO_PATTERNS = "[redacted: no patterns]"
const NEAR = 4096 // bytes: a marker can only follow a file this close to CAP (a record is far smaller)
const capped = new Set() // files that hold the truncated marker
const looked = new Set() // files whose tail this process has already checked for the marker

const text = (value, max = 200) => (typeof value === "string" ? value.slice(0, max) : "")

function kitDir(root) {
  try {
    const conf = fs.readFileSync(path.join(root, "agent-kit.conf"), "utf8")
    const found = conf.match(/^KIT_DIR=["']?([^"'\r\n]+)["']?/m)
    return found ? found[1] : "_docs/agent-kit"
  } catch {
    return "_docs/agent-kit"
  }
}

// The compiled patterns, or null when they cannot be read or one would match everything.
function loadPatterns(root) {
  try {
    const file = path.join(root, kitDir(root), "scripts", "secret-patterns.txt")
    const lines = fs.readFileSync(file, "utf8").split("\n").map((l) => l.replace(/\r$/, "")).filter((l) => l !== "")
    if (lines.length === 0) return null
    const regexes = lines.map((l) => new RegExp(l, "g"))
    return regexes.some((r) => new RegExp(r.source).test("")) ? null : regexes
  } catch {
    return null
  }
}

function redact(root, value) {
  const regexes = loadPatterns(root)
  if (!regexes) return null
  let out = value
  for (const regex of regexes) out = out.replace(regex, "[redacted]")
  return out.length > MAX_PATTERN ? out.slice(0, MAX_PATTERN - 3) + "..." : out
}

// Only whitelisted fields are ever copied. Returns null for events that are not permission events.
function toRecord(event) {
  const name = event && event.type
  if (typeof name !== "string" || !name.startsWith("permission.")) return null
  const p = event.properties || {}
  const time = new Date().toISOString()
  const asked = name === "permission.asked" // permission.updated is the older shape of the same request
  if (asked || name === "permission.updated") {
    const kind = asked ? p.permission : p.type
    const patterns = [].concat((asked ? p.patterns : p.pattern) ?? []).filter((x) => typeof x === "string")
    if (typeof p.id === "string" && typeof p.sessionID === "string" && typeof kind === "string") {
      return { event: "ask", tool: "opencode", time, sessionID: text(p.sessionID), id: text(p.id), type: text(kind), pattern: patterns.join(" "), source: name }
    }
  }
  if (name === "permission.replied") {
    const id = p.requestID ?? p.permissionID
    const response = p.reply ?? p.response
    if (typeof p.sessionID === "string" && typeof id === "string" && typeof response === "string") {
      return { event: "reply", tool: "opencode", time, sessionID: text(p.sessionID), id: text(id), response: text(response, 20), source: name }
    }
  }
  return { event: "unknown", tool: "opencode", time, source: text(name) } // the name only, never the payload
}

const hasMarker = (file) => fs.readFileSync(file, "utf8").slice(-1000).includes('"event":"truncated"')

function append(root, record) {
  const dir = path.join(root, ".agent-kit", "logs", "permissions")
  fs.mkdirSync(dir, { recursive: true })
  const file = path.join(dir, record.time.slice(0, 10) + ".jsonl")
  const line = JSON.stringify(record) + "\n"
  let size = 0
  try {
    size = fs.statSync(file).size
  } catch {
    size = 0
  }
  // The marker check comes before any append of a normal record: nothing follows a marker,
  // not in this process (capped) and not after a restart (first look at the file, or near the cap).
  if (!capped.has(file) && size > 0 && (!looked.has(file) || size > CAP - NEAR)) {
    looked.add(file)
    if (hasMarker(file)) capped.add(file)
  }
  if (capped.has(file)) return
  if (size + Buffer.byteLength(line) <= CAP) {
    fs.appendFileSync(file, line)
    return
  }
  capped.add(file) // the first record that does not fit ends the day's log
  if (!hasMarker(file)) {
    fs.appendFileSync(file, JSON.stringify({ event: "truncated", tool: "opencode", time: record.time }) + "\n")
  }
}

export const PermissionLog = async ({ client, directory }) => {
  const root = directory || process.cwd()
  let warned = false
  const warn = (message) =>
    Promise.resolve()
      .then(() => client.app.log({ body: { service: "permission-log", level: "warn", message } }))
      .catch(() => {})
  return {
    event: async ({ event }) => {
      try {
        const record = toRecord(event)
        if (!record) return
        if (record.event === "ask") {
          const clean = redact(root, record.pattern)
          record.pattern = clean === null ? NO_PATTERNS : clean
          if (clean === null && !warned) {
            warned = true
            await warn("secret-patterns.txt could not be read, so patterns are logged as redacted")
          }
        }
        append(root, record)
      } catch (error) {
        await warn("permission-log failed: " + text(String((error && error.message) || error)))
      }
    },
  }
}
