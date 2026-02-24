from app.main import get_vector


def test_get_vector_error_handling():
    # Test how it handles encoder service being down
    # We mock the ENCODER_URL to something unreachable
    from app import main

    original_url = main.ENCODER_URL
    main.ENCODER_URL = "http://localhost:9999"

    vector = get_vector("test")
    assert vector == {}

    main.ENCODER_URL = original_url


# More comprehensive tests would mock the APIs
