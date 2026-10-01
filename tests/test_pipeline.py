def test_aggregate_consistent_observations():
    from src.returns_manager.vision_pipeline import aggregate_observations
    from src.returns_manager.vision import VisionObservation

    observations = [
        VisionObservation(
            image_ref="image1.jpg",
            identity_observation="match",
            observed_state="opened_unused",
            confidence=0.9,
        ),
        VisionObservation(
            image_ref="image2.jpg",
            identity_observation="match",
            observed_state="opened_unused",
            confidence=0.8,
        ),
    ]

    result = aggregate_observations(observations)

    assert result is not None
    assert result.identity_observation == "match"
    assert result.observed_state == "opened_unused"
    assert result.confidence == 0.8


def test_aggregate_conflicting_identity_becomes_uncertain():
    from src.returns_manager.vision_pipeline import aggregate_observations
    from src.returns_manager.vision import VisionObservation

    observations = [
        VisionObservation(
            image_ref="image1.jpg",
            identity_observation="match",
            observed_state="opened_unused",
            confidence=0.9,
        ),
        VisionObservation(
            image_ref="image2.jpg",
            identity_observation="uncertain",
            observed_state="opened_unused",
            confidence=0.5,
        ),
    ]

    result = aggregate_observations(observations)

    assert result is not None
    assert result.identity_observation == "uncertain"


def test_aggregate_conflicting_state_becomes_uncertain():
    from src.returns_manager.vision_pipeline import aggregate_observations
    from src.returns_manager.vision import VisionObservation

    observations = [
        VisionObservation(
            image_ref="image1.jpg",
            identity_observation="match",
            observed_state="opened_unused",
            confidence=0.9,
        ),
        VisionObservation(
            image_ref="image2.jpg",
            identity_observation="match",
            observed_state="damaged",
            confidence=0.7,
        ),
    ]

    result = aggregate_observations(observations)

    assert result is not None
    assert result.observed_state == "uncertain"