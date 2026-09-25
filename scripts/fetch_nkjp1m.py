#!/usr/bin/env python3
"""Fetch and strictly validate the pinned NKJP1M tagged-frequency table.

The previous ENIAM web raw endpoint returned a tiny non-tabular response in
CI. This helper stays on the same official ENIAM revision and uses routes
available on this GitLab host. It validates the file before the frequency
audit can consume it.

Acquisition order:
1. verify the pinned public GitLab file page;
2. official GitLab web archive for that exact commit/path;
3. official GitLab web raw endpoint;
4. shallow Git fetch/show of the exact pinned commit and path.

Acceptance requires UTF-8 text, non-HTML content, a plausible minimum size,
exactly seven tab-separated columns on every data row, a positive integer
frequency in column 4, and a minimum number of valid rows.

The optional --expected-sha256 is intended for the later immutable source
lock. It is deliberately optional in this first migration step so the first
successful acquisition can establish and record the verified SHA-256.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path
from typing import BinaryIO
from urllib.parse import quote

import requests


GITLAB_BASE = "https://git.nlp.ipipan.waw.pl"
PROJECT = "wojciech.jaworski/ENIAM"
REVISION = "be02836cf3aa0286ad8961d2e4528cdc2f72d044"
FILE_PATH = "resources/NKJP1M/NKJP1M-tagged-frequency.tab"
EXPECTED_COLUMNS = 7
DEFAULT_MIN_BYTES = 1_000_000
DEFAULT_MIN_ROWS = 10_000
TIMEOUT = (30, 180)
USER_AGENT = "CleverKeys-langpack-pl/NKJP1M-fetch"

HTML_MARKERS = (
    b"<!doctype html",
    b"<html",
    b"<head",
    b"<body",
    b"<form",
    b"access denied",
    b"sign in",
    b"login",
    b"gateway timeout",
    b"service unavailable",
)


class AcquisitionError(RuntimeError):
    pass


def project_web_url() -> str:
    return f"{GITLAB_BASE}/{PROJECT}"


def raw_web_url() -> str:
    return f"{project_web_url()}/-/raw/{REVISION}/{FILE_PATH}"


def archive_web_url() -> str:
    return (
        f"{project_web_url()}/-/archive/{REVISION}/"
        f"ENIAM-{REVISION}.tar.gz"
    )


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})
    return session


def reject_response(response: requests.Response, *, archive: bool = False) -> None:
    if response.status_code >= 400:
        preview = response.text[:160].replace("\n", " ")
        raise AcquisitionError(
            f"HTTP {response.status_code} from {response.url}: {preview!r}"
        )
    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" in content_type or "application/xhtml" in content_type:
        kind = "archive" if archive else "file"
        raise AcquisitionError(
            f"Unexpected HTML {kind} response from {response.url}: {content_type!r}"
        )


def fetch_metadata(session: requests.Session) -> dict:
    """Best-effort verification of the pinned public GitLab file page.

    This host currently returns 404 for /api/v4, so the page check is
    informational. The acquisition URLs still hard-pin both commit and path,
    and the downloaded bytes are independently validated and hashed.
    """
    url = f"{project_web_url()}/-/blob/{REVISION}/{FILE_PATH}"
    response = session.get(url, timeout=TIMEOUT, allow_redirects=True)
    if response.status_code >= 400:
        raise AcquisitionError(
            f"Pinned file page returned HTTP {response.status_code}: {response.url}"
        )
    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type:
        raise AcquisitionError(
            f"Pinned file page returned unexpected content-type: {content_type!r}"
        )
    return {
        "page_url": response.url,
        "commit_id": REVISION,
        "file_path": FILE_PATH,
        "content_type": content_type,
    }


def stream_to_path(response: requests.Response, target: Path) -> int:
    response.raise_for_status()
    written = 0
    with target.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                handle.write(chunk)
                written += len(chunk)
    return written


def attempt_archive(session: requests.Session, target: Path) -> str:
    with session.get(
        archive_web_url(),
        params={"path": "resources/NKJP1M"},
        timeout=TIMEOUT,
        stream=True,
        allow_redirects=True,
    ) as response:
        reject_response(response, archive=True)
        with tempfile.NamedTemporaryFile(
            prefix="nkjp1m-", suffix=".tar.gz", delete=False
        ) as temp:
            archive_path = Path(temp.name)
            stream_to_path(response, archive_path)

    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            matches = [
                member
                for member in archive.getmembers()
                if member.isfile() and member.name.endswith("/" + FILE_PATH)
            ]
            if len(matches) != 1:
                raise AcquisitionError(
                    f"Archive contained {len(matches)} candidates for {FILE_PATH!r}"
                )

            extracted = archive.extractfile(matches[0])
            if extracted is None:
                raise AcquisitionError("Target archive member is not readable")

            with target.open("wb") as output:
                while True:
                    chunk = extracted.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            return matches[0].name
    finally:
        archive_path.unlink(missing_ok=True)


def attempt_raw_lfs(session: requests.Session, target: Path) -> None:
    with session.get(
        raw_web_url(),
        timeout=TIMEOUT,
        stream=True,
        allow_redirects=True,
    ) as response:
        reject_response(response)
        stream_to_path(response, target)


def attempt_git_clone(session: requests.Session, target: Path) -> None:
    del session
    import subprocess

    with tempfile.TemporaryDirectory(prefix="nkjp1m-git-") as work:
        repo_dir = Path(work) / "repo"
        clone = subprocess.run(
            [
                "git", "clone", "--filter=blob:none", "--no-checkout",
                "--depth", "1", project_web_url() + ".git", str(repo_dir)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if clone.returncode != 0:
            raise AcquisitionError(
                f"git clone failed: {clone.stderr[-400:]}"
            )

        fetch = subprocess.run(
            ["git", "-C", str(repo_dir), "fetch", "--depth", "1", "origin", REVISION],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if fetch.returncode != 0:
            raise AcquisitionError(
                f"git fetch pinned revision failed: {fetch.stderr[-400:]}"
            )

        show = subprocess.run(
            ["git", "-C", str(repo_dir), "show", f"{REVISION}:{FILE_PATH}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if show.returncode != 0:
            raise AcquisitionError(
                f"git show pinned file failed: {show.stderr.decode(errors='replace')[-400:]}"
            )
        target.write_bytes(show.stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def looks_like_error_page(path: Path) -> None:
    prefix = path.read_bytes()[:8192].lower()
    if any(marker in prefix for marker in HTML_MARKERS):
        raise AcquisitionError(
            f"Downloaded content looks like HTML/login/error page: {prefix[:160]!r}"
        )


def validate_table(path: Path, *, min_bytes: int, min_rows: int) -> dict:
    size = path.stat().st_size
    if size < min_bytes:
        raise AcquisitionError(
            f"NKJP file is implausibly small: {size} bytes < minimum {min_bytes}"
        )

    looks_like_error_page(path)

    data_rows = 0
    comment_rows = 0
    empty_rows = 0
    header_like_rows = 0
    exact_column_rows = 0
    frequency_sum = 0

    with path.open("rb") as handle:
        for line_no, raw_line in enumerate(handle, 1):
            if not raw_line.strip():
                empty_rows += 1
                continue

            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise AcquisitionError(
                    f"NKJP file is not valid UTF-8 at line {line_no}"
                ) from exc

            stripped = line.rstrip("\r\n")
            if not stripped.strip():
                empty_rows += 1
                continue
            if stripped.lstrip().startswith("#"):
                comment_rows += 1
                continue

            fields = stripped.split("\t")
            if len(fields) != EXPECTED_COLUMNS:
                raise AcquisitionError(
                    f"Invalid NKJP row at line {line_no}: expected "
                    f"{EXPECTED_COLUMNS} columns, found {len(fields)}"
                )
            exact_column_rows += 1

            try:
                frequency = int(fields[3])
            except ValueError:
                if data_rows == 0 and fields[3].strip().lower() in {"frequency", "freq"}:
                    header_like_rows += 1
                    continue
                raise AcquisitionError(
                    f"Invalid NKJP frequency at line {line_no}: {fields[3]!r}"
                )

            if frequency <= 0:
                raise AcquisitionError(
                    f"Non-positive NKJP frequency at line {line_no}: {frequency}"
                )

            data_rows += 1
            frequency_sum += frequency

    if data_rows < min_rows:
        raise AcquisitionError(
            f"NKJP validation found only {data_rows} data rows < minimum {min_rows}"
        )

    return {
        "size_bytes": size,
        "data_rows": data_rows,
        "comment_rows": comment_rows,
        "empty_rows": empty_rows,
        "header_like_rows": header_like_rows,
        "rows_with_exactly_7_columns": exact_column_rows,
        "frequency_sum": frequency_sum,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--out-sha256", type=Path, required=True)
    parser.add_argument("--out-provenance", type=Path, required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--min-bytes", type=int, default=DEFAULT_MIN_BYTES)
    parser.add_argument("--min-rows", type=int, default=DEFAULT_MIN_ROWS)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out_sha256.parent.mkdir(parents=True, exist_ok=True)
    args.out_provenance.parent.mkdir(parents=True, exist_ok=True)

    session = make_session()
    provenance = {
        "status": "starting",
        "source": {
            "gitlab_base": GITLAB_BASE,
            "project": PROJECT,
            "project_web_url": project_web_url(),
            "file_path": FILE_PATH,
            "pinned_revision": REVISION,
        },
        "metadata": {},
        "attempts": [],
        "validation_policy": {
            "expected_columns": EXPECTED_COLUMNS,
            "min_bytes": args.min_bytes,
            "min_rows": args.min_rows,
            "reject_html_error_pages": True,
        },
    }

    try:
        try:
            provenance["metadata"] = fetch_metadata(session)
        except Exception as exc:
            provenance["attempts"].append(
                {
                    "method": "repository-files-metadata",
                    "status": "failed",
                    "error": str(exc),
                }
            )

        attempts = (
            ("repository-archive", lambda: attempt_archive(session, args.out)),
            ("gitlab-web-raw", lambda: attempt_raw_lfs(session, args.out)),
            ("git-pinned-commit", lambda: attempt_git_clone(session, args.out)),
        )

        last_error: Exception | None = None
        acquired_by = None
        archive_member = None

        for method, action in attempts:
            try:
                archive_member = None
                result = action()
                acquired_by = method
                if isinstance(result, str):
                    archive_member = result
                provenance["attempts"].append(
                    {
                        "method": method,
                        "status": "downloaded",
                        "archive_member": archive_member,
                    }
                )
                break
            except Exception as exc:
                last_error = exc
                provenance["attempts"].append(
                    {
                        "method": method,
                        "status": "failed",
                        "error": str(exc),
                    }
                )
        else:
            raise AcquisitionError(
                f"All official GitLab acquisition methods failed: {last_error}"
            )

        validation = validate_table(
            args.out,
            min_bytes=args.min_bytes,
            min_rows=args.min_rows,
        )
        local_sha256 = sha256(args.out)
        expected_sha256 = (
            args.expected_sha256.lower() if args.expected_sha256 else None
        )
        if expected_sha256 and local_sha256 != expected_sha256:
            raise AcquisitionError(
                f"SHA-256 mismatch: expected {expected_sha256}, got {local_sha256}"
            )

        provenance.update(
            {
                "status": "validated",
                "acquired_by": acquired_by,
                "sha256": local_sha256,
                "expected_sha256": expected_sha256,
                "remote_content_sha256": provenance["metadata"].get("content_sha256"),
                "remote_size": provenance["metadata"].get("size"),
                "validation": validation,
            }
        )

        args.out_sha256.write_text(
            f"{local_sha256}  {args.out.name}\n",
            encoding="utf-8",
        )
        args.out_provenance.write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(provenance, ensure_ascii=False, indent=2))
        return 0

    except Exception as exc:
        provenance["status"] = "failed"
        provenance["validation_error"] = str(exc)
        args.out_provenance.write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        args.out.unlink(missing_ok=True)
        raise SystemExit(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
