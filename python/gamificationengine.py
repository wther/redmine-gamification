import datetime


class GamificationEngine:
    """Class assigning points to analyzed meta data"""

    def __init__(self, config=None):
        """
        Initialize gamification engine by setting the weights for the rewarding system

        :param config:Configuration containing the rewarding system
        """

        if config is None:
            self.config = {
                "time": {
                    "default": -1,
                    "for_update": 0.8,
                    "for_update_on_weekday": 0.2,
                    "for_at_least_3": 0.3,
                    "for_max_8": 0.5,
                    "for_distibuted": 0.2
                },
                "update": {
                    "default": -1,
                    "for_any_comment": 0.6,
                    "for_done_ratio": 0.4,
                    "for_attachment": 0.5,
                    "for_nice_comments": 0.3,
                    "for_story_teller": 0.2
                },
                # Only reward/penalize for activity in trackers 1..8,
                # these are the default redmine trackers (Bug, Feature, etc.)
                "trackers": [i for i in range(8)]
            }
        else:
            self.config = config

    def fill_in_time_points(self, user_id, user, entry_meta, issue_meta, all_days, points):
        """ Method filling in the points for good behavior on time entry"""

        # Look at time entries
        for key, day in user['days'].items():

            time_points = [self.config["time"]["default"]]
            reasons = []

            # Updated time?
            if day['total_hours'] > 0:
                time_points += [self.config["time"]["for_update"]]
            elif self.config["time"]["for_update"] > 0.0:
                reasons += ["Penalty for no logged time"]

            if day['day_of_week'] < 5:
                time_points += [self.config["time"]["for_update_on_weekday"]]
            elif self.config["time"]["for_update_on_weekday"] > 0.0:
                reasons += ["Penalty for logging on weekend"]

            # Worked at least 5 hours?
            dummy_entry_suspected = 3 - min(3, day['total_hours'])
            time_points += [self.config["time"]["for_at_least_3"] * (1 / (1 + dummy_entry_suspected))]

            if day['total_hours'] < 3 and self.config["time"]["for_at_least_3"] > 0.0:
                reasons += ["Penalty for logging less than 3 hours"]

            # Probably only for today?
            overtime_suspected = max(0, day['total_hours'] - 8)
            time_points += [self.config["time"]["for_max_8"] * (1 / (1 + overtime_suspected))]

            if day['total_hours'] > 8 and self.config["time"]["for_max_8"] > 0.0:
                reasons += ["Penalty for logging more than 8 hours"]

            # How many issues have hours ?
            issues_with_hours = len([issue for id, issue in day.items() if isinstance(id, int) and issue['hours'] > 0.0])
            time_points += [self.config["time"]["for_distibuted"] * (1 - 1/(1 + issues_with_hours))]

            if issues_with_hours > 1 and self.config["time"]["for_distibuted"] > 0.0:
                reasons += ["Reward for logging time on multiple issues"]

            if key in points[user_id]:
                points[user_id][key]['time_points'] = {
                    'sum': sum(time_points),
                    'reasons': reasons
                }

    def fill_in_update_points(self, user_id, user, entry_meta, issue_meta, all_days, points):
        """ Method filling in the points for good behavior on updates"""

        # Look at updates
        for key, day in user['days'].items():
            update_points = [self.config["update"]["default"]]
            reasons = []

            # Any comments to any of the updated issues?
            comment_sum = sum([issue['comment_length'] for id, issue in day.items() if isinstance(id, int)])

            if comment_sum > 0:
                update_points += [self.config["update"]["for_any_comment"]]
            elif self.config["update"]["for_any_comment"] > 0:
                reasons += ["Penalty for not commenting on issues"]

            # All issues excluding Meeting and above ids
            issues = [id for id, issue in day.items() if isinstance(id, int) and id in issue_meta and issue_meta[id]['tracker'] in self.config["trackers"]]

            # How many issues have logged time but no done ratio?
            without_done_ratio = len([issue_id for issue_id in issues if not issue_meta[issue_id]['done_ratio'] > 0 and day[issue_id]['hours'] > 0])

            # It's OK to have one issue without done ratio
            without_done_ratio = max(0, without_done_ratio - 1)

            update_points += [self.config["update"]["for_done_ratio"] * (1/(1+without_done_ratio))]
            if without_done_ratio > 0:
                reasons += ["Penalty for not updating done ratio on issue with logged time"]

            # Were there any attachments?
            number_of_attachments = sum([issue['attachments'] for id, issue in day.items() if id in issue_meta])

            update_points += [self.config["update"]["for_attachment"] * (1 - (1/(1+number_of_attachments)))]

            if number_of_attachments > 0 and self.config["update"]["for_attachment"] > 0.0:
                reasons += ["Reward for attaching files"]

            # Were there any nicely formatted comments ?
            formatted_comments = sum([issue['comment_extra'] for id, issue in day.items() if id in issue_meta])

            update_points += [self.config["update"]["for_nice_comments"] * (1 - (1/(1+formatted_comments/2)))]

            if formatted_comments > 0 and self.config["update"]["for_nice_comments"] > 0:
                reasons += ["Reward for nicely formatted comments"]

            # Rewards loads of comments
            comment_extra = max(0, comment_sum - 150)

            update_points += [self.config["update"]["for_story_teller"] * (1 - (1/(1+number_of_attachments/50)))]

            if comment_extra > 0 and self.config["update"]["for_story_teller"] > 0.0:
                reasons += ["Reward for being a story teller"]

            if key in points[user_id]:
                points[user_id][key]['update_points'] = {
                    'sum': sum(update_points),
                    'reasons': reasons
                }

    def calculate_points(self, entry_meta, issue_meta):
        """
        Calculates to gamification points for the days in the entry meta

        :param entry_meta: Entry meta analyzed
        :param issue_meta: Issue meta analyzed
        :return: Dictionary with points assigned to users and days
        """

        # Assigned points
        points = {}

        # Which days count ?
        all_days = []
        for user in entry_meta.values():
            for day, data in user["days"].items():
                if data["day_of_week"] < 5:
                    all_days += [day]

        all_days = set(all_days)

        for user_id, user in entry_meta.items():

            default_point_dict = {
                'time_points': {'sum': self.config["time"]["default"], 'reasons': ["Absent"]},
                'update_points': {'sum': self.config["update"]["default"], 'reasons': ["Absent"]},
            }

            points[user_id] = {day: default_point_dict.copy() for day in all_days}

            self.fill_in_time_points(user_id, user, entry_meta, issue_meta, all_days, points)
            self.fill_in_update_points(user_id, user, entry_meta, issue_meta, all_days, points)

        return points
