# orchestrator.py
from flask import Flask, request, jsonify
from threading import Thread
from comms import send_json_to_service, SERVICE_URLS
import time
from ai_wrapper import generate_reply
from flask_cors import CORS 
import json


app = Flask(__name__)

LANGUAGE = "ROMANIAN"
previous_answererd = True


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
SYSTEM_PROMT_USER = SYSTEM_PROMT_USER + f"all responses must be in {LANGUAGE} language."

SYSTEM_PROMT_INTERNAL = ""



USER_RESPONSE_STACK = []  # make sure this exists
SERVICE_NAME = "orchestrator"



def list_to_string(lst, sep="\n"):
    return sep.join(str(x) for x in lst)


def parse_main_request_data(text: str):
    global USER_RESPONSE_STACK

    # Build history string
    previous_messages = list_to_string(USER_RESPONSE_STACK)
    print("previous messages:", previous_messages)

    # Add current user message to stack
    USER_RESPONSE_STACK.append(text)

    # Build user prompt
    user_prompt = previous_messages + "\nUSER: " + text if previous_messages else text

    # Call the model
    raw_response = generate_reply(
        SYSTEM_PROMT_USER,
        user_prompt
    )
    print("orchestrator raw response:", raw_response)

    # Parse JSON
    try:
        response = json.loads(raw_response)
    except json.JSONDecodeError:
        print("WARNING: Orchestrator returned non-JSON. Using raw text as immediate_response.")
        response = {"immediate_response": raw_response}

    print("orchestrator parsed response:", response)

    # CASE 1: MODEL ASKS A QUESTION → keep context, do NOT clear stack
    if "question" in response:
        question = response["question"]
        USER_RESPONSE_STACK.append(question)
        print("orchestrator question to user:", question)
        return response

    # CASE 2: NO QUESTION → this is a final answer with actions
    # Dispatch work to services here, then clear context.

    if "inventory" in response:
        inv = response["inventory"]
        send_json_to_service("inventory", "/receive" , inv)


    if "legal" in response:
        leg = response["legal"]
        send_json_to_service("legal", "/input", response)

    if "immediate_response" in response:
        print("orchestrator immediate response:", response["immediate_response"])
        # TODO: send this back to the user

    # Now that everything is resolved for this “thread”, clear context
    print("Conversation for this request resolved, clearing USER_RESPONSE_STACK")
    USER_RESPONSE_STACK.clear()

    return response



@app.route("/text", methods=["POST", "GET"])
def handle_text():
    if request.method == "POST":
        data = request.json
        print("Received data:", data)
        message = data.get("msg", "")
        print("Processing message:", message) 
        parse_main_request_data(message)

        return jsonify({"received": data}), 200
    return jsonify({"message": "Send a POST request with JSON data."}), 200




def send_message(data):
    send_json_to_service("frontend", "/send_message", data)

    



@app.route("/legal_recieve", methods=["POST"])
def legal_recieve():
    data = request.json
    print("Received legal data:", data)

    return jsonify({"status": "received", "data": data}), 200



@app.route("/receive_inventory", methods=["GET"])
def receive_inventory():
    # receive inventory data from inventory service
    data = request.json
    print("Received inventory data:", data)

    return jsonify({"status": "received", "data": data}), 200




if __name__ == "__main__":

    app.run(port=5001, debug=True)


    
    
    
    
