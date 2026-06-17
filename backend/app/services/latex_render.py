import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from ..config import settings


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "latex_templates"


def _latex_escape(value) -> str:
    if value is None:
        return ""
    text = str(value)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def _make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["tex"] = _latex_escape
    return env


_env = _make_env()


def render_tex(template_type: str, context: dict) -> str:
    name = {"private": "private.tex.j2", "federal": "federal.tex.j2", "state": "state.tex.j2"}.get(template_type)
    if not name:
        raise ValueError(f"Unknown template_type: {template_type}")
    template = _env.get_template(name)
    return template.render(**context)


def compile_pdf(tex_source: str, out_dir: str | os.PathLike) -> tuple[str, str, int, list[str]]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex[:12]
    work = Path(tempfile.mkdtemp(prefix=f"resume-{job_id}-"))
    try:
        tex_path = work / "resume.tex"
        tex_path.write_text(tex_source, encoding="utf-8")
        warnings: list[str] = []
        cmd = [
            "tectonic",
            "-X",
            "compile",
            "--keep-logs",
            "--keep-intermediates",
            "--outdir",
            str(work),
            str(tex_path),
        ]
        env = os.environ.copy()
        env.setdefault("TECTONIC_CACHE_DIR", "/tmp/tectonic-cache")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
        except FileNotFoundError:
            raise RuntimeError(
                "tectonic binary not found inside the backend container. "
                "Confirm the Dockerfile installed it."
            )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "")[-1500:]
            raise RuntimeError(f"tectonic failed (exit {proc.returncode}):\n{tail}")
        pdf_src = work / "resume.pdf"
        if not pdf_src.exists():
            raise RuntimeError("tectonic ran but produced no PDF")
        final_pdf = out_dir / f"resume-{job_id}.pdf"
        final_tex = out_dir / f"resume-{job_id}.tex"
        shutil.copy2(pdf_src, final_pdf)
        shutil.copy2(tex_path, final_tex)
        pages = _count_pdf_pages(final_pdf)
        if proc.stderr:
            for line in proc.stderr.splitlines():
                if re.search(r"warning", line, re.IGNORECASE):
                    warnings.append(line.strip())
        return str(final_tex), str(final_pdf), pages, warnings[:20]
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _count_pdf_pages(pdf_path: Path) -> int:
    try:
        data = pdf_path.read_bytes()
        # Count /Type /Page occurrences (not /Pages)
        count = len(re.findall(rb"/Type\s*/Page(?!s)", data))
        return max(count, 1)
    except Exception:
        return 0


def ats_check(pdf_path: str, keywords: list[str]) -> dict:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return {"available": False}
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        lower = text.lower()
        missing = [k for k in keywords if k and k.lower() not in lower]
        ligatures = any(ch in text for ch in "ﬀﬁﬂﬃﬄ")
        return {
            "available": True,
            "pages": len(reader.pages),
            "missing_keywords": missing,
            "has_ligatures": ligatures,
            "chars": len(text),
        }
    except Exception as e:
        return {"available": True, "error": str(e)}
