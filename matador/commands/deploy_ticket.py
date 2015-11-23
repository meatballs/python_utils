#!/usr/bin/env python
from .command import Command
from matador.commands.deployment import *
from matador.session import Session
import subprocess
import os
import shutil


class DeployTicket(Command):

    def _add_arguments(self, parser):
        parser.prog = 'matador deploy-ticket'
        parser.add_argument(
            '-e', '--environment',
            type=str,
            required=True,
            help='Agresso environment name')

        parser.add_argument(
            '-t', '--ticket',
            type=str,
            required=True,
            help='Ticket name')

        parser.add_argument(
            '-c', '--commit',
            type=str,
            default='none',
            help='Branch name')

        parser.add_argument(
            '-p', '--packaged',
            type=bool,
            default=False,
            help='Whether this deployment is part of a package')

    def _checkout_ticket(self, repo_folder, ticket_folder, commit):

        subprocess.run([
            'git', '-C', repo_folder, 'checkout', commit],
            stderr=subprocess.STDOUT,
            stdout=open(os.devnull, 'w'),
            check=True)

        src = os.path.join(repo_folder, 'deploy', 'tickets', self.args.ticket)
        shutil.copytree(src, ticket_folder)

    def _cleanup(self, ticket_folder):
        shutil.rmtree(ticket_folder)

    def _execute(self):
        Session.set_environment(self.args.environment)
        proj_folder = Session.project_folder
        repo_folder = Session.matador_repository_folder
        ticket_folder = os.path.join(
            Session.matador_tickets_folder, self.args.ticket)
        Session.ticket_folder = ticket_folder

        if not self.args.packaged:
            Session.update_repository()

        if self.args.commit == 'none':
            commit = subprocess.check_output(
                ['git', '-C', proj_folder, 'rev-parse', 'HEAD'],
                stderr=subprocess.STDOUT).decode('utf-8').strip('\n')
        else:
            commit = self.args['commit']

        self._logger.debug(commit)

        self._checkout_ticket(repo_folder, ticket_folder, commit)

        deploy_file = os.path.join(ticket_folder, 'deploy.py')
        try:
            from importlib.machinery import SourceFileLoader
            SourceFileLoader('deploy', deploy_file).load_module()
        finally:
            self._cleanup(ticket_folder)
