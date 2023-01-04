import pytest

garmin_ativities_data = [
    {
        "api_responce": {
            "activityType": {"typeKey": "running"},
            "duration": 3600,
            "calories": 250,
            "distance": 10,
            "elevationGain": 50,
            "maxHR": 170,
            "averageHR": 150,
            "startTimeLocal": "2022-01-01T09:00:00",
            "steps": 5000,
            "movingDuration": 3500,
        },
        "test_metadata": {
            "sport": "Running",
            "separate": False,
            "estimated_steps": 11,
        }
    },
    {
        "api_responce": {
            "activityType": {"typeKey": "cycling"},
            "duration": 3600,
            "calories": 300,
            "distance": 30,
            "elevationGain": 75,
            "maxHR": 190,
            "averageHR": 170,
            "startTimeLocal": "2022-01-03T09:00:00",
            "steps": 7500,
            "movingDuration": 3500,
        },
        "test_metadata": {
            "sport": "Bicycle",
            "separate": False,
            "estimated_steps": 0,
        }
    },
]


@pytest.fixture(scope="module", params=garmin_ativities_data)
def garmin_activity_data(request):
    return request.param["api_responce"], request.param["test_metadata"]
