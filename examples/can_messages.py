# Example on how to use the DBC file to encode and decode messages

from odrive_can import get_dbc

db = get_dbc()  # load default DBC

# get message
msg = db.get_message_by_name("Axis0_Heartbeat")
print("Message:", msg)

# Both numeric and string values are accepted, choices are converted to integers
encoded_msg = msg.encode(
    {
        "Axis_Error": "INVALID_STATE",
        "Axis_State": 11,
        "Motor_Error_Flag": 0,
        "Encoder_Error_Flag": 0,
        "Controller_Error_Flag": 0,
        "Trajectory_Done_Flag": 0,
    }
)
print("Encoded:", encoded_msg)
# decode message

decoded_msg = msg.decode(encoded_msg)
print("Decoded:", decoded_msg)
