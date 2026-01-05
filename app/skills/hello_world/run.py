def execute(input_data: dict) -> dict:
    """
    Simple hello world function.
    Input: {"name": "World"}
    Output: {"message": "Hello, World!"}
    """
    name = input_data.get("name", "World")
    return {
        "message": f"Hello, {name}!",
        "status": "success",
        "timestamp": "now"
    }
