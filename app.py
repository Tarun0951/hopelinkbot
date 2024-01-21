import streamlit as st
import joblib
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.stem import PorterStemmer
from twilio.rest import Client
from bardapi import Bard
from bardapi import BardCookies

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC4210b2b2167007571b29f0c1d2f85aef'
TWILIO_AUTH_TOKEN = 'ef2d8a3d89962d974cc331ca159c9c29'
TWILIO_PHONE_NUMBER = '
RECIPIENT_PHONE_NUMBER = '

# Load the model
model = joblib.load('new_model.pkl')
vectorizer = joblib.load('tfidf2.pkl')

# Define the stop words
stop_words = set(ENGLISH_STOP_WORDS)

def preprocess(inp):
    inp = inp.lower()  # Convert to lowercase
    inp = ' '.join(inp.split())  # Replace multiple spaces with a single space
    inp = ' '.join([word for word in inp.split() if word not in stop_words])  # Tokenize the sentence
    ps = PorterStemmer()
    inp = ' '.join([ps.stem(i) for i in inp.split()])  # Stemming
    return inp  # Return the processed text

def detect_suicide(input_text):
    processed_text = preprocess(input_text)
    predict = model.predict(vectorizer.transform([processed_text]).toarray())  # Convert to a dense numpy array
    return predict[0]

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(message):
    # Send an SMS
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=RECIPIENT_PHONE_NUMBER
    )
    return message.sid

# Initialize Bard API
cookie_dict = {
    "__Secure-1PSID": 
    "__Secure-1PSIDTS": 
    # Any cookie values you want to pass session object.
}
bard = BardCookies(cookie_dict=cookie_dict)

# Set page configuration with a dark background
st.set_page_config(
    page_title="AI Companion and Suicide Detection",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded",  # or "collapsed"
)

# Add a dark background
st.markdown(
    """
    <style>
        body {
            background-color: #2a2a2a;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar with navigation buttons
selected_option = st.sidebar.radio("Navigation", ["Suicide Detection", "AI Companion"])

# Suicide Detection Section
if selected_option == "Suicide Detection":
    st.title("Suicide Detection and SMS Notification")
    st.write("Use this application to detect possible suicide risk in text messages. An SMS alert will be sent if a risk is detected.")

    # Add a button with a custom icon to send the user message and detect suicide
    if st.button("Send", key="send_button"):
        # Get user input
        user_input = st.text_area("User Message", key="user_input")

        # Perform suicide detection
        result = detect_suicide(user_input)
        st.session_state.user_messages = [ user_input]

        if result == 'suicide':
            message = "Possible suicide risk detected. Seek help immediately."
            st.session_state.chatbot_messages = [ message]
            # Send an SMS alert
            send_sms(message)
            st.warning(message)  # Display the warning on the screen
        else:
            message = "No suicide risk detected."
            st.session_state.chatbot_messages = [ message]
            st.success(message)  # Display the success message on the screen

        # Display the chat interface for suicide detection
        st.subheader("Chat:")
        for user_msg, chatbot_msg in zip(st.session_state.user_messages, st.session_state.chatbot_messages):
            st.markdown(f"👤 User: {user_msg}")
            st.markdown(f"🤖 Chatbot: {chatbot_msg}")

# AI Companion Section
elif selected_option == "AI Companion":
    st.title("AI Companion")
    st.image("mh-logo.jpeg",width=200)
    changes='''
        <style>
        [data-testid="stAppViewContainer"]
        {
        background-color:rgba(255,255,255,0.05);
        background-size:fit;
        }
        .st-bx {
        background-color: rgba(255, 255, 255, 0.05);
        }

        /* .css-1hynsf2 .esravye2 */

        html {
        background: transparent;
        }
        div.esravye2 > iframe {
            background-color: transparent;
        }
        </style>
        '''
    
    st.markdown(changes,unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def generate_response(prompt):
        response = bard.get_answer(prompt)['content']
        return response

    if prompt := st.text_input("I'm here to support you. Remember, you're not alone. What's on your mind?", key="input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"👤 User: {prompt}")

        response = generate_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(f"🤖 Assistant: {response}")
