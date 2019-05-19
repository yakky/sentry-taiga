"""
sentry_taiga.plugin
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 by RochSystems.
:license: MIT, see LICENSE for more details.
"""

from django import forms
from sentry.plugins.bases.issue import IssuePlugin
from django.utils.translation import ugettext_lazy as _

from taiga import TaigaAPI

import sentry_taiga

class TaigaOptionsForm(forms.Form):
    taiga_url = forms.CharField(
        label=_('Taiga URL'),
        widget=forms.TextInput(attrs={'placeholder':
                                      'e.g. https://tree.taiga.io'}),
        help_text=_('Enter the URL for your Taiga server'),
        required=True,
        initial='https://tree.taiga.io')

    taiga_api = forms.CharField(
        label=_('Taiga API'),
        widget=forms.TextInput(attrs={'placeholder':
                                      'e.g. https://api.taiga.io'}),
        help_text=_('Enter the Taiga API URL'),
        required=True,
        initial='https://api.taiga.io')

    taiga_username = forms.CharField(
        label=_('Taiga User Name'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. user@example.com'}),
        help_text=_('Enter your Taiga User name'),
        required=True)

    taiga_password = forms.CharField(
        label=_('Taiga Password'),
        widget=forms.PasswordInput(attrs={'placeholder': 'e.g. your password'}),
        help_text=_('Enter your Taiga User password'),
        required=True)

    taiga_project = forms.CharField(
        label=_('Taiga Project Slug'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. project-slug'}),
        help_text=_('Enter your project slug.'),
        required=True)

    taiga_labels = forms.CharField(
        label=_('Issue Labels'),
        widget=forms.TextInput(attrs={'placeholder': 'e.g. high, bug'}),
        help_text=_('Enter comma separated labels you '
                    'want to auto assign to issues.'),
        required=False)


class TaigaPlugin(IssuePlugin):
    author = 'Sentry'
    author_url = 'http://sentry.io/'
    version = sentry_taiga.VERSION
    description = "Integrate Taiga issues by linking a repository to a project"
    resource_links = [
        ('Bug Tracker', 'https://github.com/getsentry/sentry-taiga/issues'),
        ('Source', 'https://github.com/getsentry/sentry-taiga'),
    ]

    slug = 'taiga'
    title = _('Taiga')
    conf_title = title
    conf_key = 'taiga'
    project_conf_form = TaigaOptionsForm

    def is_configured(self, request, project, **kwargs):
        return bool(self.get_option('taiga_project', project))

    def get_new_issue_title(self, **kwargs):
        return _('Create Taiga Issue')

    def create_issue(self, request, group, form_data, **kwargs):

        url = self.get_option('taiga_url', group.project)
        api = self.get_option('taiga_api', group.project)
        username = self.get_option('taiga_username', group.project)
        password = self.get_option('taiga_password', group.project)
        project_slug = self.get_option('taiga_project', group.project)
        labels = self.get_option('taiga_labels', group.project)

        tg = TaigaAPI(host=api)

        try:
            tg.auth(username=username, password=password)
        except Exception as e:
            raise forms.ValidationError(_('Error Communicating '
                                        'with Taiga: %s') % (e,))

        project = tg.projects.get_by_slug(slug=project_slug)
        if project is None:
            raise forms.ValidationError(_('No project found in Taiga with slug %s') %
                                        (project_slug,))

        default_issue_status = project.default_issue_status
        priority = project.default_priority
        issue_type = project.default_issue_type
        severity = project.default_severity

        if default_issue_status is None:
            raise forms.ValidationError(_('Project %s has no default status. '
                'Set the default issue status in Taiga') % (project.name,))

        if not labels:
            labels = ''
        data = {
            'subject': form_data['title'],
            'status': default_issue_status,
            'description': form_data['description'],
            'priority': priority,
            'issue_type': issue_type,
            'severity': severity,
            'tags': [label.strip() for label in labels.split(",") if label]
            }

        issue = project.add_issue(**data)

        return issue.ref


    def get_issue_label(self, group, issue_id, **kwargs):
        return 'TG-%s' % issue_id

    def get_issue_url(self, group, issue_id, **kwargs):
        url = self.get_option('taiga_url', group.project)
        slug = self.get_option('taiga_project', group.project)

        return '%s/project/%s/issue/%s' % (url, slug, issue_id)
