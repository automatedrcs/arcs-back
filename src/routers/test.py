from fastapi import FastAPI

test_router = FastAPI()

@test_router.get("/api/data")
def get_data():
    return {
        "message": "Data fetched successfully",
        "data": {
            "example_key": "example_value"
        }
    }
