import pytest
from ai_vault_cli.planning.planner import Planner

def test_create_plan():
    planner = Planner()
    result = planner.create_plan("demo")
    assert result is not None
    assert "demo" in result.title

def test_plan_summary():
    planner = Planner()
    planner.create_plan("demo")
    summary = planner.get_summary("demo")
    assert summary is not None
    assert "summary" in summary

def test_plan_invalid_slug():
    planner = Planner()
    with pytest.raises(ValueError):
        planner.create_plan("")  # Invalid slug should raise an error

def test_plan_with_existing_slug():
    planner = Planner()
    planner.create_plan("demo")
    with pytest.raises(FileExistsError):
        planner.create_plan("demo")  # Should raise an error if plan already exists