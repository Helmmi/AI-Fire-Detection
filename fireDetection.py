import cv2

import numpy as np

import os

if os.path.exists("screenshot.jpg"):
    os.remove("screenshot.jpg")


import google.generativeai as genai

import mysql.connector
from mysql.connector import Error

import firebase_admin
from firebase_admin import db,credentials
import http.client, urllib

def json(n):
    
    db.reference("/").update({"nb":n})

def notifi():
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": "aiq3dmdxhsspnt885ki78c5y5ac7qw",
    "user": "uym9zzs28mwjt39166j59ioiw5296c",
    "message": "there are fire detected",
  }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    print("message sent successfully")



genai.configure(api_key="AIzaSyAgt3MVvSVFGLjfE2V8omB9dN26je5FZJ8")

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
)
def update_db(n):
    try:
        connection = mysql.connector.connect(
               host="sql5.freesqldatabase.com",
               user="sql5743894",
               password="LYkJyD2cSy",
               database="sql5743894"
        )

        if connection.is_connected():
            cursor = connection.cursor()
            if(n==1):
                query = "UPDATE fire SET nbsecurity = 1"
            elif(n==-1):
                query = "UPDATE fire SET nbsecurity = -1"
            
            cursor.execute(query)
            connection.commit()
            print("Data inserted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Example usage
#insert_data("Fire Sensor 1", 75, True)

def detect_fire(frame):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Define the range of fire colors in HSV
    lower_fire = np.array([0, 150, 150])
    upper_fire = np.array([10, 255, 255])
    lower_fire2 = np.array([170, 150, 150])
    upper_fire2 = np.array([180, 255, 255])
    # Create masks for detecting fire colors
    mask1 = cv2.inRange(hsv, lower_fire, upper_fire)
    mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
    # Combine masks
    mask = cv2.bitwise_or(mask1, mask2)

    # Count the number of non-zero pixels in the mask
    fire_detected = cv2.countNonZero(mask)

    return fire_detected

# Main function to run the fire detection
def main():
    # Start video capture (0 for default camera)
    cred = credentials.Certificate("firedetection-ffa1f-firebase-adminsdk-ou3ny-01e3d4a13f.json")
    
    firebase_admin.initialize_app(cred,{"databaseURL":"https://firedetection-ffa1f-default-rtdb.firebaseio.com/"})
    json(0)
    cap = cv2.VideoCapture(0)
    #adr="https://192.168.104.200:8080/video"
    #cap.open(adr)
    i=0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        
        fire_count = detect_fire(frame)

        
        if fire_count > 1000:  
            i+=1
            if i==20:
                cv2.imwrite("screenshot.jpg", frame)
                cv2.putText(frame, "Fire Detected!", (10, 30) , cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                sample_file = genai.upload_file(path="screenshot.jpg", display_name="Sample drawing")
                response = model.generate_content(["answer me by yes or no is there any fire in this image.", sample_file])
                ch = response.text
                if response.text.find("Yes") == 0:
                    print("fire detected")
                    #update_db(1)
                    notifi()
                    json(1)
                    i=0


  
                else:
                    print(response.text)
                    os.remove("screenshot.jpg")
                    i=0


            #insert_data(True)

        # Show the video frame
        cv2.imshow("Fire Detection", frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            update_db(-1)
            json(-1)
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()
    json(-1)

if __name__ == "__main__":
    main()
