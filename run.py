from app import create_app
from app.extensions import db

app = create_app()

print(app.url_map)

@app.route("/")
def home():
    return {
        "status": "success"
    }

@app.route("/test-db")
def test_db():

    try:

        db.session.execute(db.text("SELECT 1"))

        return {
            "status": "success",
            "message": "PostgreSQL connection successful"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }, 500
    

if __name__ == "__main__":
    app.run(debug=True)