from garmin_daily import Activity


def test_activity_init(garmin_activity_marked):
    activity = Activity.init_from_garmin_activity(garmin_activity_marked[0])
    assert activity.activity_type == garmin_activity_marked[0]["activityType"]["typeKey"]
    assert activity.duration == garmin_activity_marked[0]["duration"]
    assert activity.calories == garmin_activity_marked[0]["calories"]
    assert activity.distance == garmin_activity_marked[0]["distance"]
    assert activity.elevation_gain == garmin_activity_marked[0]["elevationGain"]
    assert activity.max_hr == garmin_activity_marked[0]["maxHR"]
    assert activity.average_hr == garmin_activity_marked[0]["averageHR"]
    assert activity.start_time == garmin_activity_marked[0]["startTimeLocal"]
    assert activity.steps == garmin_activity_marked[0]["steps"]
    assert activity.moving_duration == garmin_activity_marked[0]["movingDuration"]
    assert activity.non_walking_steps is None
    assert str(activity) == garmin_activity_marked[1]["str"]


def test_activity_estimate_steps(garmin_activity_marked):
    activity = Activity.init_from_garmin_activity(garmin_activity_marked[0])
    activity.sport = garmin_activity_marked[1]["sport"]
    assert activity.estimate_steps() == garmin_activity_marked[1]["estimated_steps"]
