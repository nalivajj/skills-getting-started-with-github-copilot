"""
Tests for the Mergington High School API activities endpoints.
Uses Arrange-Act-Assert pattern with pytest.
"""

from urllib.parse import quote
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert expected_activity in data
        assert isinstance(data[expected_activity]["participants"], list)

    def test_get_activities_contains_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert required_fields.issubset(activity_data.keys()), (
                f"Activity '{activity_name}' missing required fields"
            )

    def test_chess_club_has_initial_participants(self, client):
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert data["Chess Club"]["participants"] == expected_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_successfully(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name, safe='')}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_student_already_signed_up_returns_error(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name, safe='')}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name, safe='')}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_increments_participant_count(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "newprogrammer@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{quote(activity_name, safe='')}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        assert len(activities_response.json()[activity_name]["participants"]) == initial_count + 1


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_successfully(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name, safe='')}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_remove_missing_participant_returns_404(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "missing@mergington.edu"
        assert email not in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name, safe='')}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
