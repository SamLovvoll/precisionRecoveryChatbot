from flask import Flask, request
from decouple import config
import openai

app = Flask(__name__)

# array to hold conversation history message by message
conversation = []

@app.route('/')
def home():
    global conversation
    # set the api key
    openai.api_key = config('KEY')

    # reset conversation
    conversation = [{"role": "system", "content": "you are a healthcare assistant talking to a stroke patient. if you think the user is currently having a stroke, please refer them to call a healthcare professional"}]

    # create a new section in the history txt document and write the pre-prompt to it
    with open("/home/Slovvoll/mysite/history.txt", mode="a") as f:
        f.write("\nNEW THREAD: \n")
        f.write("PROMPT: " + conversation[0]["content"] + "\n")

    # start the loop of prompt-answer
    return prompt()

# this runs to prompt the user and display the current conversation thread
@app.route('/prompt')
def prompt():
    global conversation

    # convert conversation into a single string that can be passed into the HTML as message history
    message_history = ''

    # for each message, parse the role and message, then line break
    for message in conversation[1:]:
        message_history += "<br><b>" + message["role"] + ":</b><br>" + message["content"] + "<br>"

    # this is pretty much the entire website right here
    HOME_HTML = """
     <html><body>
         <h2>Chatting With ChatGPT</h2>
         <form action="/answer">
             MESSAGE HISTORY:<br>{convo}<br>enter your prompt for ChatGPT: <input type='text' name='prompt'><br>
             <input type='submit' value='Continue'>
         </form>
     </body></html>""".format(convo=message_history)
    return HOME_HTML

# this is run shortly to get the response from the ai and returns the html from prompt()
@app.route('/answer')
def answer():
    global conversation

    # get User's prompt from url
    inp = request.args.get('prompt', '')

    # add the prompt to the conversation history (required for chatGPT to see the prompt)
    conversation.append({"role": "user", "content": inp})

    # get ChatGPT's response
    response = chat_with_gpt()

    # add the response to the conversation history
    conversation.append({"role": "assistant", "content": response})

    # add user prompt and ai response to conversation history
    with open("/home/Slovvoll/mysite/history.txt", mode="a") as f:
        f.write("USER: " + inp+"\n")
        f.write("BOT: " + response+"\n")

    return prompt()

# get response from chatGPT
def chat_with_gpt():
    global conversation

    model_engine = "gpt-3.5-turbo"

    # gives the entire conversation history, including the most recent prompt as context
    completion = openai.ChatCompletion.create(
        model=model_engine,
        messages = conversation
    )

    message = completion.choices[0].message.content
    return message