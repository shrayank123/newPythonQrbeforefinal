
from datetime import datetime
import json
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from twilio.rest import Client
from dataOfDef import *
# Initialize webcam
capture = cv2.VideoCapture(0)




# Time settings
timeAbsent = "7:30 AM"
eight_am = datetime.strptime("08:00 AM", "%I:%M %p")

# Twilio credentials
account_sid = 'AC310c16b1a8835ef1218e6545bb2265d4'
auth_token = '99562340ba0b5fda7feb0d87e4fa2a5a'


# def send_message(text,teacher):
#     client = Client(account_sid, auth_token)
#
#     message = client.messages.create(
#         from_='whatsapp:+14155238886',
#         body=text,
#         to=f'whatsapp:{teacher}'
#     )
#
#     print(message.sid)

def clear_json_file(file_path):
    try:
        with open(file_path, 'w') as f:
            json.dump({}, f)
    except FileNotFoundError:
        print(f"Error: JSON file '{file_path}' not found.")
def clear_txt_file(file):
    with open(file, 'w') as f:
        pass  # The pass statement is a placeholder indicating no operation is needed


def ensure_json_exists(path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({}, f)


def load_json(path):
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def update_present_students():
    data = load_json(sis_path)
    present_students = {'Jc1': [], 'Jc2': []}

    for key, value in data.items():
        if value['state'] == 'present':
            if key.startswith("Jc1"):
                present_students['Jc1'].append(value['name'])
            elif key.startswith("Jc2"):
                present_students['Jc2'].append(value['name'])

    # save_json(std_class_path, present_students)

def LoadPresentAbsent(class_path,present,absent):
  with open(class_path,'r') as f:
          dataX = json.load(f)
          for x in dataX:
                  present.append(dataX[x]['name'])
          for x in Jc1Def:
              if x not in present:
                  absent.append(x)
          print(absent)
          print(present)


# Ensure the JSON files exist
ensure_json_exists(sis_path)
ensure_json_exists(Jc1_path)
ensure_json_exists(Jc2_path)


# Clear JSON files at the start
clear_json_file(sis_path)
clear_json_file(Jc1_path)
clear_json_file(Jc2_path)

# Clear txt files at the start
clear_txt_file(Jc1Txt)

while True:
    ret, frame = capture.read()

    # Flip the frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)

    qr_info = decode(frame)

    if len(qr_info) > 0:
        qr = qr_info[0]
        data = qr.data.decode()
        rect = qr.rect
        polygon = qr.polygon

        cv2.putText(frame, data, (rect.left, rect.top), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
        frame = cv2.rectangle(frame, (rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height),
                              (0, 255, 255), 5)
        frame = cv2.polylines(frame, [np.array(polygon)], True, (255, 0, 0), 5)

        student = data[-(len(data) - 4):]

        now = datetime.now()
        formatted_time = now.strftime("%I:%M %p")
        formatted_date = now.strftime("%Y-%m-%d")

        parsed_time = datetime.strptime(formatted_time, "%I:%M %p")
        state = 'absent' if parsed_time.time() > eight_am.time() else 'present'

        new_data = {
            data: {
                'name': student,
                "time": formatted_time,
                'date': formatted_date,
                'state': state
            }
        }

        student_data = load_json(sis_path)
        student_data.update(new_data)
        save_json(sis_path, student_data)

        if data.startswith("Jc1"):
            jc1_data = load_json(Jc1_path)
            jc1_data.update({data: new_data[data]})
            save_json(Jc1_path, jc1_data)
        elif data.startswith("Jc2"):
            jc2_data = load_json(Jc2_path)
            jc2_data.update({data: new_data[data]})
            save_json(Jc2_path, jc2_data)

        update_present_students()

    cv2.imshow('webcam', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
