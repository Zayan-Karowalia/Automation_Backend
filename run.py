from app import create_app

app = create_app()

print(app.url_map)

@app.route("/")
def home():
    return {
        "status": "success"
    }

if __name__ == "__main__":
    app.run(debug=True)