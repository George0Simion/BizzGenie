# orchestrator.py
from flask import Flask, request, jsonify
from threading import Thread
from comms import send_json_to_service, SERVICE_URLS
import time
from ai_wrapper import generate_reply
app = Flask(__name__)


USER_RESPONSE_STACK = []




SERVICE_NAME = "orchestrator"
SYSTEM_PROMT_USER = """You are an AI agents manager called Orchestrator. You will receive messages from a small bussiness owner user and commmand the other AI services (legal, predictor , invetory , notification agent)
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
    
    You must format the response as a JSON object with one of the following structures:
    1. If you know what actions to take, and it is clear what to do, respond with:
    {
        "inventory": {
            "action": "add stock" / "remove stock"",
            "details": {
                "item_id": "this will be a string identifying the item's name",
                "quantity": "integer representing how many items to add or remove",
                "quantity_unit": "string representing the unit of measurement (e.g., 'pieces', 'kg', 'liters')"
            }
        },
        "legal": {
            "subject": "string describing what legal information is needed"}  

        "immediate_response": "string with a message acknowledging the user request and summarizing the actions taken"
    }
    
    2. If you need more information from the user to decide what actions to take, respond with:
    {
        "question": "string with a message asking the user for more information"
    }

"""


SYSTEM_PROMT_INTERNAL = ""






def parse_main_request_data(text):
    response = generate_reply(
        SYSTEM_PROMT_USER,
        USER_RESPONSE_STACK + [text]
    )
    
    if "question" in response:
        USER_RESPONSE_STACK.append(text)
        parse_main_request_data("The user says: " + response["question"])
        
        
    # if the user request is not clear ask for more information
    
    
    


    
    
    print("response from AI:", response)
    with open("last_orchestrator_response.json", "w") as f:
        f.write(response)
    return response    
    







@app.route("/text", methods=["POST", "GET"])
def handle_text():
    if request.method == "POST":
        data = request.json
        parse_main_request_data("Am cumparat rosii")

        return jsonify({"received": data}), 200
    return jsonify({"message": "Send a POST request with JSON data."}), 200



if __name__ == "__main__":

    app.run(port=5001, debug=True)
    

    
    
    
    
