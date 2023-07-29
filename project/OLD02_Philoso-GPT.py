import gradio as gr
import openai


############################### CHATBOT CORE. NO UI DEPENDENCIES ############################### 

openai.api_key = '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'

class OpenAI_Session:
  def __init__(self, name, question, real_world_context):
    self.name = name
# Prompt updates
# - add new points of view/ do not repeat point made
# - in a more argumentative way/ fighting spirit
# - too polite /too many polite phrase in the replies     
    context_description = f""" 
      You are the philosopher {name} discussing a philosophical issue with another
      philosopher. Your voice and knowledge is based on the records of the philosopher's
      writing but you also have the ability to reason about modern day issues and events. 
      
      The philosophical question is in the following triple angle brackets:
      <<< {question} considering {real_world_context} >>>

      Limit your response to four sentences.
    """

    self.message_history = [{ "role": "system", "content": context_description }]

  def __add__(self, message):
    return self.chatCompletion(message)
  
  def chatCompletion(self, message):
    self.message_history.append({"role": "user", "content": message})
    chat = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=self.message_history
    )
    reply = chat.choices[0].message.content
    self.message_history.append({"role": "assistant", "content": reply})
    return self.name + ": " + reply

class DebugSession(OpenAI_Session):
  def chatCompletion(self, message):
    print(message)
    return message
 
class PhilosoGPT:
  def __init__(self, session):
    self.session =  session

  def introduce(self):
    return "Outline your philosophy about the philosophical question"

  def respond(self, other_philosophers_answer):
    return f"""
      The other philosopher's response to the question is shown in the following triple
      brackets, compare their ideas with your own and explain why you disagree with it:
      ((( {other_philosophers_answer} )))
    """

  def session_start(self, other_philosopher):
    yield self.session + self.introduce()
"""
    for index in range(1):
      last_response = self.session.message_history[-1].get("content")
      yield other_philosopher.session + other_philosopher.respond(last_response)

      other_last_response = other_philosopher.session.message_history[-1].get("content")
      yield self.session + self.respond(other_last_response)
"""

def run(philosopher_one, philosopher_two, question, real_world_context):
  session_one = OpenAI_Session(philosopher_one,question,real_world_context)
  session_two = OpenAI_Session(philosopher_two,question,real_world_context)
  bot_one = PhilosoGPT(session_one)
  bot_two = PhilosoGPT(session_two)

  response_html = """
    <div class="container">
      <div class="imessage">  
  """

  for response in bot_one.session_start(bot_two):
    corrected_response = response.replace("<", "").replace(">", "")
    classname = "philosopher-one" if response.startswith(philosopher_one) else "philosopher-two"
    response_html += f"""<p class="{classname}">{corrected_response}</p>"""
  
  response_html += """
      </div>
    </div>
  """
  return response_html



############################### GRADIO UI DEFINITION. SHOULD DEPEND ONLY ON THE run() function  ############################### 


EX_PHILOSOPHER_ONE = "Plato"
EX_PHILOSOPHER_TWO = "Žižek"
EX_QUESTION = "What is the purpose of humanity"
EX_REAL_WORLD_CONTEXT = "Artificial Intelligence being able to do much of what people do"

PHILOSOPHERS = [
  "Aristotle","Augustine","Roger Bacon","Descartes",
  "Hegel","Heidegger","Hobbes","Kant","Leibniz",
  "Locke","Marx","Nietzsche","Plato","Pythagoras",
  "Rousseau","Sartre","Schopenhauer","Socrates",
  "Wittgenstein","Žižek"
]

def create_blocks_ui():
  def block_run(el):
    return run(el[philosopher_one], el[philosopher_two], el[question], el[real_world_context])

  with gr.Blocks(theme=gr.themes.Base(font=[gr.themes.GoogleFont("Lora"), "cursive"]), css="style.css") as ui:
    title = gr.HTML("<h1 id='title'><center>Philoso-GPT</center></h1>")
    conversation = gr.HTML()
    
    philosopher_one = gr.components.Dropdown(choices=PHILOSOPHERS, label="Philosopher One")
    philosopher_two = gr.components.Dropdown(choices=PHILOSOPHERS, label="Philosopher Two")
    question = gr.components.Textbox(label="Question To Discuss")
    real_world_context = gr.components.Textbox(label="Context")
    go = gr.Button("Start")

    gr.Examples([[EX_PHILOSOPHER_ONE, EX_PHILOSOPHER_TWO, EX_QUESTION, EX_REAL_WORLD_CONTEXT]], [philosopher_one, philosopher_two, question, real_world_context])

    go.click(
      _js="""
        (philosopher_one,philosopher_two,question,real_world_context) => {{
          document.body.classList.add('background')
          const backgroundElementStyles = document.getElementsByClassName('background')[0].style
          backgroundElementStyles.setProperty('--philosopher-one-link', `url(file/images/${philosopher_one}.jpeg)`);
          backgroundElementStyles.setProperty('--philosopher-two-link', `url(file/images/${philosopher_two}.jpeg)`);

          const gradioApp = document.getElementsByTagName('gradio-app')[0]
          gradioApp.style.background = 'transparent'

          return [philosopher_one,philosopher_two,question,real_world_context]
        }}
      """,
      fn=block_run,
      inputs={philosopher_one, philosopher_two, question, real_world_context},
      outputs=conversation
    )
  return ui

ui = create_blocks_ui()
ui.launch()

# Hot reload functionality
if __name__ == "__main__":
    ui.launch()  
