import gradio as gr
import openai



############################### TECHNIBOT CORE. NO UI DEPENDENCIES ############################### 

# key = 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
openai.api_key = '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'

class OpenAI_Session:
    """This class has an non-traditional, but simple syntax:  It returns the response when a request is added.  
        session = OpenAI_Session("You are rude intellectual who makes jokes about other people's stupidity")
        print(session + "Can you explain relativity") # Prints the response to the question, 
                # E.g. "Yes, I can. It is relatively easy. The question is if you could understand".   
    """
    def __init__(self, name, question, real_world_context):
        """context_description is a description of which role the ChaptGPT agent should take, such as helpful, conscise, creative, etc. 
        replacements is a dictionary of phrases to replaced in the returned string"""
        context_description = f""" 
              You are the philosopher {name} discussing a philosophical issue with another
              philosopher. Your voice and knowledge is based on the records of the philosopher's
              writing but you also have the ability to reason about modern day issues and events. 
              
              The philosophical question is in the following triple angle brackets:
              <<< {question} considering {real_world_context} >>>

              Limit your response to four sentences.
          """

# add new points of view/ do not repeat point made
# in a more argumentative way/ fighting spirit
# too polite /too many polite phrase in the replies        
        self.name = name
        self.message_history = [{ "role": "system", "content": context_description }]

    def __add__(self, message):
        return self.chatCompletion(message)
    
    def chatCompletion(self, message):
        self.message_history.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.message_history)
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

        for index in range(3):
          last_response = self.session.message_history[-1].get("content")
          #yield self.session + other_philosopher.respond(last_response)
          yield other_philosopher.session + other_philosopher.respond(last_response)

          other_last_response = other_philosopher.session.message_history[-1].get("content")
          yield self.session + self.respond(other_last_response)


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
  "Abelard","Anaximander","Anselm","Aquinas","Aristotle","Augustine",
  "Roger Bacon","Francis Bacon","Bentham","Berkeley","Carnap",
  "Democritus","Deleuze","Derrida","Descartes","Fichte","Frege",
  "Hegel","Heidegger","Heraclitus","Hobbes","Hume","Husserl","James",
  "Kant","Leibniz","Locke","Marx","Mill","Nietzsche","Ockham",
  "Parmenides","Peirce","Plato","Plotinus","Pythagoras","Quine",
  "Rawls","Reid","Rousseau","Russell","Sartre","Schelling",
  "Schopenhauer","Duns Scotus","Socrates","Spinoza","Wittgenstein",
  "Zeno of Lea","Žižek"
]

def create_blocks_ui():
    def block_run(el):
        return run(el[philosopher_one], el[philosopher_two], el[question], el[real_world_context])
  
    with gr.Blocks(theme=gr.themes.Base(), css="style.css") as ui:
        gr.Markdown("""<h1><center>Philoso-GPT</center></h1>""")
        philosopher_one = gr.components.Dropdown(choices=PHILOSOPHERS, label="First Philosopher")
        philosopher_two = gr.components.Dropdown(choices=PHILOSOPHERS, label="Second Philosopher")
        question = gr.components.Textbox(label="Philosophical Question")
        real_world_context = gr.components.Textbox(label="Real Life Context")

        go = gr.Button("Start")
        examples = gr.Examples([[EX_PHILOSOPHER_ONE, EX_PHILOSOPHER_TWO, EX_QUESTION, EX_REAL_WORLD_CONTEXT]], [philosopher_one, philosopher_two, question, real_world_context])

        #conversation = gr.components.Markdown(value="TBD", label="Analysis")
        conversation = gr.HTML(
          """
            <div class="container">
              <div class="imessage">  
                <p class="philosopher-two">It was loud. We just laid there and said &ldquo;is this an earthquake? I think this is an earthquake.&rdquo;</p>
                <p class="philosopher-one">Like is this an earthquake just go back to sleep</p>
              </div>
            </div>
          """)  
        go.click(fn=block_run, inputs={philosopher_one, philosopher_two, question, real_world_context}, outputs=conversation),
    return ui

ui = create_blocks_ui()
ui.launch()

# For hot reload functionality
if __name__ == "__main__":
    ui.launch()  
