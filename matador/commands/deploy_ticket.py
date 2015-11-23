#!/usr/bin/env python
from .command import Command
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
            default='master',
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
            stdout=open(os.devnull, 'w'))
        src = os.path.join(repo_folder, 'deploy', 'tickets', self.args.ticket)
        shutil.copytree(src, ticket_folder)

    def _cleanup(self, ticket_folder):
        shutil.rmtree(ticket_folder)

    def _execute(self):
        repo_folder = Session.matador_repository_folder
        ticket_folder = os.path.join(
            Session.matador_tickets_folder, self.args.ticket)

        if not self.args.packaged:
            Session.update_repository()
        self._checkout_ticket(repo_folder, ticket_folder, self.args.commit)

        os.chdir(ticket_folder)
        import deploy

        self._cleanup(ticket_folder)
