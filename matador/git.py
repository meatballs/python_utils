import logging
from dulwich.client import LocalGitClient
from dulwich.index import build_index_from_tree
from dulwich.objects import format_timezone
from time import strftime, gmtime
import re

logger = logging.getLogger(__name__)


def stage_file(repo, file):
    file_path = str(file.relative_to(repo.path))
    repo.stage(file_path)


def commit(repo, message):
    message = bytes(message, encoding='UTF-8')
    repo.do_commit(message)


def fetch_all(source_repo, target_repo, remote_name=None):
    if remote_name is None:
        remote_name = 'origin'

    refs = LocalGitClient().fetch(source_repo.path, target_repo)

    for key, value in refs.items():
        key = key.replace(
            b'heads', b'remotes/%s' % bytes(remote_name, encoding='UTF-8'))
        target_repo.refs[key] = value


def checkout(repo, ref=None):
    if ref is None:
        ref = repo.head()
    index = repo.index_path()
    tree_id = repo[ref].tree
    build_index_from_tree(repo.path, index, repo.object_store, tree_id)
    return [repo.object_store.iter_tree_contents(tree_id)]


def full_ref(repo, ref):
    refs = repo.refs.keys()
    for ref_type in ['refs/heads/', 'refs/tags/']:
        full_ref = ref_type + ref
        if bytes(full_ref, encoding='ascii') in refs:
            ref = full_ref
    return ref


def substitute_keywords(text, repo, ref):
    new_text = ''
    expanded_ref = full_ref(repo, ref)

    try:
        sha = repo.refs[bytes(expanded_ref, encoding='ascii')]

        commit = repo.get_object(sha)
        commit_time = strftime('%Y-%m-%d %H:%M:%S', gmtime(commit.commit_time))
        timezone = format_timezone(
            commit.commit_timezone).decode(encoding='ascii')
        commit_timestamp = commit_time + ' ' + timezone
        author = commit.author.decode(encoding='ascii')

        if ref.startswith('refs/tags'):
            version = 'Tag %s (%s)' % (ref, commit.id)
        else:
            version = commit.id

        substitutions = {
            'version': version,
            'date': commit_timestamp,
            'author': author
        }

        for line in text.splitlines(keepends=True):
            for key, value in substitutions.items():
                rexp = '%s:.*' % key
                line = re.sub(rexp, '%s: %s' % (key, value), line)
            new_text += line

    except KeyError:
        logger.error('%s is not a valid branch or tag' % ref)

    return new_text
