import importlib.util
from pathlib import Path

import pytest

import ki_serverentwicklung as cli

_ERD_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_erd.py"
_ERD_SPEC = importlib.util.spec_from_file_location("generate_erd", _ERD_SCRIPT)
assert _ERD_SPEC is not None and _ERD_SPEC.loader is not None
_ERD_MODULE = importlib.util.module_from_spec(_ERD_SPEC)
_ERD_SPEC.loader.exec_module(_ERD_MODULE)


def test_load_plan_and_skill_from_documented_directories(tmp_path, monkeypatch):
    plans = tmp_path / "plans"
    skills = tmp_path / ".agent" / "skills"
    plans.mkdir()
    skills.mkdir(parents=True)
    (plans / "plan.md").write_text("plan content", encoding="utf-8")
    (skills / "example.md").write_text("skill content", encoding="utf-8")
    monkeypatch.setattr(cli, "PLANS_DIR", plans)
    monkeypatch.setattr(cli, "SKILLS_DIR", skills)
    cli._read_file.cache_clear()

    assert cli.load_plan("plan.md") == "plan content"
    assert cli.load_skill("example") == "skill content"


def test_loaders_reject_empty_and_traversal_names():
    for name in ("", "../secret", "nested/name", r"nested\name", "/tmp/file"):
        with pytest.raises(ValueError):
            cli.load_plan(name)
        with pytest.raises(ValueError):
            cli.load_skill(name)


def test_loaders_report_missing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "PLANS_DIR", tmp_path / "plans")
    monkeypatch.setattr(cli, "SKILLS_DIR", tmp_path / ".agent" / "skills")
    assert cli.load_plan("missing.md").startswith("Plan not found:")
    assert cli.load_skill("missing").startswith("Skill not found:")


def test_generated_erd_includes_order_version():
    dot = _ERD_MODULE.build_dot()
    assert '<TD ALIGN="LEFT">version</TD>' in dot
    assert '<TD ALIGN="LEFT">NOT NULL DEFAULT 1</TD>' in dot


def test_repeated_file_reads_are_cached(tmp_path, monkeypatch):
    plans = tmp_path / "plans"
    plans.mkdir()
    plan = plans / "repeat.md"
    plan.write_text("first", encoding="utf-8")
    monkeypatch.setattr(cli, "PLANS_DIR", plans)
    cli._read_file.cache_clear()

    assert cli.load_plan("repeat.md") == "first"
    plan.write_text("second", encoding="utf-8")
    assert cli.load_plan("repeat.md") == "first"
    assert cli._read_file.cache_info().hits == 1
    cli._read_file.cache_clear()
