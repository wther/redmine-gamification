import redmine
import datetime


class RedmineReader:
    """Class reading the meta data out of Redmine"""

    default_issue = {
        'hours': 0,
        'updates': 0,
        'comment_length': 0,
        'comment_extra': 0,
        'attachments': 0
    }

    def __init__(self, url, user, password, project_name, verify=True):
        """
        Initializes the Redmine reader and connects to the REST service

        :param url: Redmine url, e.g. https://redmine.com/
        :param user:User to access redmine with, e.g. admin
        :param password:Password to access redmine with, e.g. paSSw0rd
        :param project_name:Name of the project, this can be read from the URL, e.g. https://redmine.com/projects/{project}
        :param verify:Flag indicating whether to accept non-verified SSL certificates
        """

        requests_config = {
            'verify': verify
        }

        self.redmine = redmine.Redmine(
            url,
            username=user,
            password=password,
            requests=requests_config)

        self.entry_meta = {}
        self.issue_meta = {}

        # Open project
        self.project = self.redmine.project.get(project_name)


    def analyze_time_entries(self, days_backwards):
        """
        Analyzes the "time entry" resources of redmine looking for logged time
        on a daily basis

        :param days_backwards: Timedelta indicating how much time to look back, e.g. 10 days
        :return: The dict with the meta data and the set of issues it found
        """

        # Access time entries
        from_date = datetime.date.today() - datetime.timedelta(days=days_backwards)
        time_entries = self.redmine.time_entry.all(project_id=self.project.id, from_date=from_date)
        user_names = {}

        # Collect meta data on time entries, in this format:
        # user_id: {
        #  YYYY-MM-DD: {
        #   issue_id: {}
        #  }, ...
        #  total_hours: X,
        # }
        entry_meta = {}

        # This method will also return the issues referenced in the entries, this
        # will enable us not to fetch irrelevant issues in when reading issue meta
        watched_issue_ids = []

        for entry in time_entries:
            user_id = entry.user.id

            if user_id not in entry_meta:
                user_names[user_id] = entry.user.name
                entry_meta[user_id] = {
                    'days': {}
                }

            spent_on = entry.spent_on.isoformat()

            if spent_on not in entry_meta[user_id]['days']:
                entry_meta[user_id]['days'][spent_on] = {
                    'total_hours': 0,
                    'day_of_week': entry.spent_on.weekday()
                }

            day = entry_meta[user_id]['days'][spent_on]

            if entry.issue.id not in day:
                day[entry.issue.id] = self.default_issue.copy()

                watched_issue_ids += [entry.issue.id]

            day[entry.issue.id]['hours'] += entry.hours
            day['total_hours'] += entry.hours

        return entry_meta, set(watched_issue_ids), user_names

    def analyze_issues(self, entry_meta, watched_issue_ids):
        """
        Analyze issues looking for updates done by users

        :param entry_meta: Entries analyzed earlier, necessary to know which days to ignore
        :param watched_issue_ids: Issues found while analyzing the entries, necessary to know which issues to fetch
        :return: Dictionary with analyzed issue data
        """

        # This dictionary is going to be built to something like this:
        # {
        #  issue_id: {
        #    "days": {
        #      YYYY-MM-DD: ...
        #    }
        #   }
        # }
        issue_meta = {}

        issues = self.redmine.issue.all(project_id=self.project.id, include='journals', sort="id:desc", status_id="*")

        for issue in issues:

            if issue.id not in watched_issue_ids:
                continue

            # Check the all requirements are filled out
            issue_meta[issue.id] = {
                "has_estimate": hasattr(issue, 'estimated_hours') and issue.estimated_hours > 0,
                "has_category": hasattr(issue, 'category') and issue.category is not None,
                "done_ratio": hasattr(issue, 'done_ratio') and issue.done_ratio,
                "tracker": issue.tracker.id
            }

            # Check that it is updated daily
            for journal in issue.journals:
                created_on = journal.created_on.date().isoformat()

                if journal.user.id in entry_meta and created_on in entry_meta[journal.user.id]['days']:
                    day = entry_meta[journal.user.id]['days'][created_on]

                    if issue.id not in day:
                        day[issue.id] = self.default_issue.copy()

                    day[issue.id]['updates'] += 1

                    if hasattr(journal, 'notes'):
                        day[issue.id]['comment_length'] += len(journal.notes)

                        extra = False
                        for word in ["http", "+","*", "please"]:
                            if word in journal.notes.lower():
                                extra = True

                        day[issue.id]['comment_extra'] += 1

                    if hasattr(journal, 'details'):
                        attachments = [attachment for attachment in journal.details if attachment['property'] == 'attachment']
                        day[issue.id]['attachments'] += len(attachments)

        return issue_meta

