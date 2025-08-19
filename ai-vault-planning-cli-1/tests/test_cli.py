import pytest
from click.testing import CliRunner
from ai_vault_cli.cli import cli

def test_ai_init():
    runner = CliRunner()
    result = runner.invoke(cli, ['init', '/path/to/vault'])
    assert result.exit_code == 0
    assert 'Configuration created' in result.output

def test_ai_index():
    runner = CliRunner()
    result = runner.invoke(cli, ['index', '/path/to/vault'])
    assert result.exit_code == 0
    assert 'Indexing complete' in result.output

def test_ai_thread_new():
    runner = CliRunner()
    result = runner.invoke(cli, ['thread', 'new', 'demo', '--vault-path', '/path/to/vault', '--seed', 'Kickoff notes'])
    assert result.exit_code == 0
    assert 'Thread created' in result.output

def test_ai_ask():
    runner = CliRunner()
    result = runner.invoke(cli, ['ask', 'What is my next task?'])
    assert result.exit_code == 0
    assert 'Answer:' in result.output

def test_ai_chat():
    runner = CliRunner()
    result = runner.invoke(cli, ['chat', 'demo', 'What should I do next?', '--write'])
    assert result.exit_code == 0
    assert 'Chat response' in result.output

def test_ai_capture():
    runner = CliRunner()
    result = runner.invoke(cli, ['capture', 'This is a quick note', '--write'])
    assert result.exit_code == 0
    assert 'Note captured' in result.output

def test_ai_plan():
    runner = CliRunner()
    result = runner.invoke(cli, ['plan', 'demo', '--weekly', '--write'])
    assert result.exit_code == 0
    assert 'Plan created' in result.output

def test_ai_doctor():
    runner = CliRunner()
    result = runner.invoke(cli, ['doctor'])
    assert result.exit_code == 0
    assert 'Sanity check complete' in result.output