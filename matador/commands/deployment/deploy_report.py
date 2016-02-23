from pathlib import Path
from matador.session import Session
from .deployment import DeploymentCommand
from matador import git
from matador import zippey
import shutil


def _fetch_report(repo, report_path, commit_ref, target_folder):
    report = Path(repo.path, report_path)
    target_report = Path(target_folder, report.name)

    git.checkout(repo, commit_ref)

    target_report.touch()
    zippey.decode(report.open('rb'), target_report.open('wb'))

    return target_report


class DeployExceleratorReport(DeploymentCommand):

    def _execute(self):
        report_name = Path(self.args[0])
        repo_folder = Session.matador_repository_folder
        report_path = Path(
            repo_folder, 'src', 'reports', report_name,
            str(report_name) + '.xlsx')

        commit = self.args[1]
        report = _fetch_report(
            Session.matador_repo, report_path, commit,
            Session.deployment_folder)
        target_folder = (
            '//' +
            Session.environment['abwServer'] + '/' +
            Session.environment['customisedReports'])

        shutil.copy(str(report), target_folder)
