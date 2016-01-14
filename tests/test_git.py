from matador import git
from pathlib import Path
from time import strftime, gmtime
from dulwich.objects import format_timezone


def test_stage_file(repo):
    repo_folder = Path(repo.path)
    test_file = Path(repo_folder, 'test_file')
    test_file.touch()
    git.stage_file(repo, test_file)

    index = repo.open_index()
    changes = [f.decode('UTF-8') for f in index]

    assert str(test_file.relative_to(repo_folder)) in changes


def test_commit(repo):
    repo_folder = Path(repo.path)
    test_file = Path(repo_folder, 'test_file')
    test_file.touch()
    message = 'Test commit'
    repo.stage([str(test_file.relative_to(repo_folder))])

    git.commit(repo, message)

    last_commit = repo.get_object(repo.head())
    commit_message = last_commit.message
    assert commit_message == bytes(message, encoding='UTF-8')


def test_full_ref_commit(project_repo):
    head = project_repo.head().decode(encoding='ascii')
    ref = git.full_ref(project_repo, head)
    assert ref == head


def test_full_ref_branch(project_repo):
    ref = git.full_ref(project_repo, 'master')
    print(project_repo.refs.keys())
    assert ref == 'refs/heads/master'


def test_full_ref_tag(project_repo):
    ref = git.full_ref(project_repo, 'test-tag')
    assert ref == 'refs/tags/test-tag'


def test_substitute_keywords(project_repo):
    test_text = """\
        First line
        version:
        date:
        author:
        Last line"""

    commit_ref = project_repo.head()
    commit = project_repo.get_object(commit_ref)
    commit_time = strftime('%Y-%m-%d %H:%M:%S', gmtime(commit.commit_time))
    timezone = format_timezone(commit.commit_timezone).decode(encoding='ascii')
    commit_timestamp = commit_time + ' ' + timezone
    author = commit.author.decode(encoding='ascii')

    result = git.substitute_keywords(test_text, project_repo, 'master')
    expected_result = """\
        First line
        version: %s
        date: %s
        author: %s
        Last line""" % (commit_ref, commit_timestamp, author)
    assert result == expected_result

    result = git.substitute_keywords(test_text, project_repo, 'test-tag')
    expected_result = """\
        First line
        version: %s
        date: %s
        author: %s
        Last line""" % (commit_ref, commit_timestamp, author)
    assert result == expected_result

    result = git.substitute_keywords(test_text, project_repo, 'test-garbage')
    expected_result = ''
    assert result == expected_result
