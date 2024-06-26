# %% [markdown]
# 
# # based on https://til.simonwillison.net/llms/python-react-pattern
# ![image.png](attachment:image.png)

# %%
#!pip install openai httpx python-dotenv

# %%
import openai
import re
import httpx
import os
import json
from dotenv import load_dotenv

_ = load_dotenv()
from openai import OpenAI

# %%
client = OpenAI()

# %%
chat_completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello world"}]
)

chat_completion

# %%
chat_completion.choices[0].message.content

# %%
class Agent: # a generic agent
    def __init__(self, system=""):
        self.system = system # this allows user to specify a system role
        self.messages = [] # store the message history
        if self.system: # if there IS a system role set, we add it to the message history to start.
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        #model="gpt-3.5-turbo",
        completion = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0,
                        messages=self.messages)
        return completion.choices[0].message.content
    

# %%
prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_dog_weight:
e.g. average_dog_weight: Collie
returns average weight of a dog when given the breed

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weights 51 lbs

You then output:

Answer: A bulldog weights 51 lbs
""".strip()

# %%
def calculate(what):
    return eval(what)

def average_dog_weight(name):
    if name in "Scottish Terrier": 
        return("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return("a toy poodles average weight is 7 lbs")
    else:
        return("An average dog weights 50 lbs")

known_actions = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight
}

# %%
abot = Agent(prompt)# %%
result = abot("How much does a toy poodle weigh?")
print(result)

# %%
result = average_dog_weight("Toy Poodle")

# %%
result

# %%
next_prompt = "Observation: {}".format(result)

# %%
abot(next_prompt)

# %%
abot.messages

# %%
abot = Agent(prompt)

# %%
question = """I have 2 dogs, a border collie and a scottish terrier. \
What is their combined weight"""
abot(question)

# %%
next_prompt = "Observation: {}".format(average_dog_weight("Border Collie"))
print(next_prompt)

# %%
abot(next_prompt)

# %%
next_prompt = "Observation: {}".format(average_dog_weight("Scottish Terrier"))
print(next_prompt)

# %%
abot(next_prompt)

# %%
next_prompt = "Observation: {}".format(eval("37 + 20"))
print(next_prompt)

# %%
abot(next_prompt)

# %%
action_regex = re.compile(r'^Action: (\w+): (.*)$')   # python regular expression to selection action


# %%
"""
# this query fun uses list comprehension whcih I find hard to read

def query(question, max_turns=5):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_regex.match(a)
            for a in result.split('\n') 
            if action_regex.match(a)
        ]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return
"""
# %%
import re

# Define the action regular expression
action_regex = re.compile(r'^Action: (\w+): (.*)$')

def query(question, max_turns=5):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print("**Bot Command ", i , "Result: [", result, "]")

        # Initialize an empty list for actions
        actions = []

        # Split the result into lines
        lines = result.split('\n')

        # Iterate over each line and apply the regex match
        for line in lines:
            match = action_regex.match(line)
            if match:
                actions.append(match)

        if actions:
            # There is an action to run
            action, action_input = actions[0].groups() # groups is a property of the regex.Match object which is created when regex successfully matches
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} ({})".format(action, action_input))
            #this next line is what actaully calls the function
            # "action" is the string - we go into known_actions and find teh object in the dictionary that matches that string
            # because that object IS a function, we can immediately go () on it.
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return
    if i >= max_turns:
        print ("Bot couldn't come up with result in time.")
# Test the query function
question = """I have 2 dogs, a border collie and a scottish terrier. \
What is their combined weight"""
#query(question)



# %%
question = """I have 2 dogs, a border collie and a scottish terrier. \
What is the  combined weight of these dogs after pooping huge massive turds (guess how much each dog would poop as roughly 10% of that dog's weight)? 
When you have your answer, return it as a weight in kg, but then name an animal with roughly the same weight"""
query(question, max_turns=10)


# %%



