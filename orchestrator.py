# orchestrator.py
from flask import Flask, request, jsonify
from threading import Thread
from comms import send_json_to_service, SERVICE_URLS
import time
from ai_wrapper import generate_reply
app = Flask(__name__)

SERVICE_NAME = "orchestrator"
SYSTEM_PROMT = """You are an AI agents manager called Orchestrator. You will receive messages from a small bussiness owner user and commmand the other AI services (legal, predictor , invetory , notification agent)
to get their input.

    The user is running a small restaurant business.    

    The bussiness owner will tell you what they did and you must decide what actions to take.
    
    The bussinser owner is not experienced in managing a bussiness so you must think of all the implications of their actions and command the agents accordingly.

    AGENTS YOU CAN COMMAND:
    1. legal: This agent returns legal information about compliance, regulations, and policies given the subject"
    2. inventory: This agent keeps track of stock levels, adds or removes items from inventory based on user actions.
    YOUR TASK:
        The user will send simple messages you must interpret them and expand on the request to command the agents.
        The user might not think of all implications so you must think of what agents to command to fulfill the user request.
    
    You must format the response as a JSON object with the following structure:
    {
        "inventory": {
            "action": "add stock" / "remove stock"",
            "details": {
                "item_id": "string",
                "quantity": integer,
            }
        },
        "legal": {
            "subject": "string describing what legal information is needed"}  

        "immediate_response": "string with a message acknowledging the user request and summarizing the actions taken"
    }

"""









def parse_main_request_data(text):
    response = generate_reply(
        SYSTEM_PROMT,
        text
    )
    print("response from AI:", response)
    with open("last_orchestrator_response.json", "w") as f:
        f.write(response)
    return response    
    







@app.route("/text", methods=["POST", "GET"])
def handle_text():
    if request.method == "POST":
        data = request.json
        parse_main_request_data("Am cumparat 3 kilograme de rosii")

        return jsonify({"received": data}), 200
    return jsonify({"message": "Send a POST request with JSON data."}), 200



if __name__ == "__main__":

    app.run(port=5001, debug=True)
    

    
    
    
    
