from fastapi import FastAPI
app=FastAPI()
def load_data():
    with open('patient.json',"r") as file:
        data = file.read()
    return data

@app.get("/")
def name():
    return {"message":"Hello ujjwal"}
@app.get("/about")
def about():
    return {"message":"This is a FastAPI tutorial"}
@app.get("/view")
def view_data():
    data = load_data()
    return data