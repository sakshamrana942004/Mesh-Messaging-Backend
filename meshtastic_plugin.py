import meshtastic
import meshtastic.serial_interface

interface = meshtastic.serial_interface.SerialInterface()

def send_lora_message(text):

    interface.sendText(text)

def receive_lora_message(packet):

    print("LoRa message:", packet)