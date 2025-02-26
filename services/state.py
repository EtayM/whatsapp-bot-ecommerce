# services/state.py

import logging
import importlib
import json
from services.nocodb import fetch_table_records

logger = logging.getLogger(__name__)

STATES_TABLE_ID = "mv298y9fqa5019f"  # Replace with your actual table ID

class StateManager:
    def __init__(self):
        self.states = {}
        self.load_states()

    def load_states(self):
        try:
            states_data = fetch_table_records(STATES_TABLE_ID)
            logger.debug(f"States data from NocoDB: {states_data}") # Add logging
            for state_data in states_data['list']:
                state_name = state_data['Name'] # Upper camel case
                handler_module = state_data['HandlerModule'] # Upper camel case
                handler_function = state_data['HandlerFunction'] # Upper camel case
                welcome_message = state_data['WelcomeMessage'] # Upper camel case
                parameter_name = state_data.get('ParameterName')  # Get the parameter name # Upper camel case
                other_data = state_data.get('OtherData') # Get other data
                if other_data is not None:
                    other_data = json.loads(other_data)  # Safely parse JSON
                else:
                    other_data = {}

                self.states[state_name] = {
                    'handler_module': handler_module,
                    'handler_function': handler_function,
                    'welcome_message': welcome_message,
                    'parameter_name': parameter_name,
                    'other_data': other_data,
                }
            logger.info(f"Loaded states: {list(self.states.keys())}")
        except Exception as e:
            logger.error(f"Error loading states from NocoDB: {e}")
            # Consider raising an exception or exiting if state loading is critical

    def get_state(self, state_name):
        logger.debug(f"Getting state: {state_name}") # Add logging
        return self.states.get(state_name)
