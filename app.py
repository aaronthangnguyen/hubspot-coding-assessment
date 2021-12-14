import requests
import json


def app():
    events = request_get()
    post_body = get_post_body(events)
    r = request_post(post_body)
    print(f"Status code: {r.status_code}")


def request_get():
    r = requests.get(
        "https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=a0d583a81412b3c59781a73f79c7"
    )
    r_dictionary = r.json()
    events = r_dictionary["events"]

    return events


def get_post_body(events):
    sessions_by_user = {}
    post_body = {"sessionsByUser": sessions_by_user}

    for event in events[:]:
        user_id = event["visitorId"]
        if event["visitorId"] not in sessions_by_user:
            sessions_by_user[user_id] = []

        sessions = sessions_by_user[user_id]
        sessions.append(event)

    for user_id in sessions_by_user:
        sessions_by_user[user_id] = get_session_group(sessions_by_user[user_id])

    return post_body


def get_session_group(sessions):
    def if_timestamps_are_within_10_minutes(first_timestamp, second_timestamp):
        return abs(first_timestamp - second_timestamp) <= 600000

    sessions.sort(key=lambda session: session["timestamp"])
    session_group = []
    previous_timestamp = 0

    for session in sessions:
        if len(session_group) == 0:
            session_group.append(
                {
                    "duration": 0,
                    "pages": [session["url"]],
                    "startTime": session["timestamp"],
                }
            )
        elif if_timestamps_are_within_10_minutes(
            session["timestamp"], previous_timestamp
        ):
            session_group[-1]["duration"] = (
                session["timestamp"] - session_group[-1]["startTime"]
            )
            session_group[-1]["pages"].append(session["url"])
        else:
            session_group.append(
                {
                    "duration": 0,
                    "pages": [session["url"]],
                    "startTime": session["timestamp"],
                }
            )
        previous_timestamp = session["timestamp"]

    return session_group


def request_post(post_body):
    r = requests.post(
        "https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=a0d583a81412b3c59781a73f79c7",
        data=json.dumps(post_body),
    )

    return r


if __name__ == "__main__":
    app()
