# Shared helpers for scan-issue-body.sh, issue-create.sh and issue-comment.sh.
# Sourced, not run. The caller sets `set -u` and `set -o pipefail`.
#
# Issue text is untrusted. These helpers never expand, evaluate or interpret it.
# A file is read ONCE into the variable B64 as base64, because a shell variable
# cannot hold a NUL byte (it would drop it silently, and a secret could slip
# through). Every later check, the scan and the post decode the same B64, so the
# bytes checked are the bytes sent.

# read_b64 SOURCE LIMIT: read at most LIMIT+1 bytes from SOURCE (a file path, or
# "-" for standard input) into B64. Returns 1 when the read fails. One byte more
# than LIMIT is read so that callers can tell "over the limit" from "exactly at it".
read_b64() {
  local source="$1" limit="$2"
  B64=""
  if [ "$source" = "-" ]; then
    B64=$(head -c "$((limit + 1))" | base64 | tr -d '\n') || return 1
  else
    B64=$(head -c "$((limit + 1))" -- "$source" | base64 | tr -d '\n') || return 1
  fi
}

# b64_decode: write the exact bytes held in B64 to standard output.
b64_decode() {
  printf '%s' "$B64" | base64 -d
}

# b64_size: print the number of bytes held in B64.
b64_size() {
  local size
  size=$(b64_decode | wc -c) || return 1
  printf '%s' "${size//[[:space:]]/}"
}

# b64_has_nul: true when the bytes in B64 contain a NUL byte. An unreadable
# result counts as true, so a failure never looks clean.
b64_has_nul() {
  local total without
  total=$(b64_decode | wc -c) || return 0
  without=$(b64_decode | tr -d '\000' | wc -c) || return 0
  [ "${total//[[:space:]]/}" != "${without//[[:space:]]/}" ]
}

# b64_is_utf8: true when the bytes in B64 are valid UTF-8.
b64_is_utf8() {
  b64_decode | python3 -B -c 'import sys; sys.stdin.buffer.read().decode("utf-8")' 2>/dev/null
}

# ---- Used by issue-create.sh and issue-comment.sh only ----------------------
# The caller defines `die CODE MESSAGE` (print one line to standard error, exit
# CODE) and sets `here` to this folder. Exit codes: 1 gh failed, 2 bad argument
# or file, 3 the scanner refused, 4 the target issue is not allowed.

MAX_POST_BYTES=60000

# check_number N: digits only, 1 to 9 of them, no leading zero. Runs before gh.
check_number() {
  case "$1" in
    "" | *[!0-9]* | 0*) die 2 "N must be an issue number: digits only, no leading zero" ;;
  esac
  [ "${#1}" -le 9 ] || die 2 "N must have at most 9 digits"
}

# check_file_arg FILE: the path rules, checked before FILE is opened.
# One word of letters, digits and . _ / - only; under .scratch/; no "..";
# no component (the file itself or any parent folder) that is a symlink;
# the file is a regular file.
check_file_arg() {
  local file="$1" rest part path=""
  [ -n "$file" ] || die 2 "FILE is empty"
  case "$file" in
    -*) die 2 "FILE must not start with -" ;;
    *[!A-Za-z0-9._/-]*) die 2 "FILE may only use letters, digits and . _ / -" ;;
  esac
  case "$file" in
    .scratch/*) ;;
    *) die 2 "FILE must be a path under .scratch/" ;;
  esac
  case "$file" in
    *..*) die 2 "FILE must not contain .." ;;
  esac
  rest="$file"
  while [ -n "$rest" ]; do
    part="${rest%%/*}"
    if [ "$part" = "$rest" ]; then rest=""; else rest="${rest#*/}"; fi
    [ -n "$part" ] || continue
    path="${path:+$path/}$part"
    [ ! -L "$path" ] || die 2 "FILE or one of its folders is a symlink"
  done
  [ -f "$file" ] || die 2 "FILE is missing or is not a regular file"
}

# load_issue_file FILE: read FILE once (see the top of this file), apply the size
# and content rules, and leave the exact text in CONTENT (B64 holds the same bytes).
load_issue_file() {
  local size
  read_b64 "$1" "$MAX_POST_BYTES" || die 2 "cannot read FILE"
  size=$(b64_size) || die 2 "cannot measure FILE"
  [ "$size" -gt 0 ] || die 2 "FILE is empty"
  [ "$size" -le "$MAX_POST_BYTES" ] || die 2 "FILE is larger than $MAX_POST_BYTES bytes"
  if b64_has_nul; then die 2 "FILE holds a NUL byte (or cannot be checked for one)"; fi
  b64_is_utf8 || die 2 "FILE is not valid UTF-8"
  CONTENT=$(b64_decode; printf x) || die 2 "cannot read FILE"
  CONTENT="${CONTENT%x}"
  [ -n "${CONTENT//[[:space:]]/}" ] || die 2 "FILE holds only whitespace"
}

# scan_content FILE: run the scanner on the exact bytes in CONTENT (through
# standard input, not by path, so a file swapped after the read changes nothing).
# Any non-zero exit is a refusal. Only the scanner's own lines are shown, which
# never hold the matching text.
scan_content() {
  local label="$1" out code line
  out=$(bash "$here/scan-issue-body.sh" - 2>&1 < <(printf '%s' "$CONTENT"))
  code=$?
  [ "$code" -ne 0 ] || return 0
  while IFS= read -r line; do
    case "$line" in
      -:*) printf '%s\n' "$label:${line#-:}" >&2 ;;
      *) printf '%s\n' "$line" >&2 ;;
    esac
  done <<< "$out"
  die 3 "the secret scan refused FILE (exit $code); nothing was posted"
}

# print_url OUTPUT: gh prints the new URL on success. Anything else is not a
# success, so the wrapper says so without echoing the output.
print_url() {
  case "$1" in
    "" | *$'\n'* | *[[:space:]]*) die 1 "gh printed no issue URL; check GitHub before posting again (no retry was made)" ;;
    https://*) printf '%s\n' "$1" ;;
    *) die 1 "gh printed no issue URL; check GitHub before posting again (no retry was made)" ;;
  esac
}
