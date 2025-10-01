## Open AI GPT With Python and Guard Rails

A example ofhow we can connect with open ai with python and how we can create some types of guard rails for  protect our app of alucination

### First, we need export our open ai api key as an environment variable

```
export OPENAI_API_KEY='my_open_ai_api_key'

```
### Build your virtual enviroment*

```
python -m venv venv && source venv/bin/activate
```

### Load Dependecies from requirements.txt*

```
pip install -r requirements.txt

```


### We have three exmaples here:

1. **ai_chat_console_example.py =>** This example shows how we connect, send and format the response from GPT

2. **guardrail_output.py =>**  This example shows how we make a guard-rails type to format output from gpt, validating with pydantic

3. **guardrail_block_alucination =>** This example shows hoe we make a guard-rails type to protect our app from alucination

To execute the examples, execute:
1.
```
python ai_chat_console_example.py
```

2.
```
python guardrail_output.py
```

3.
```
python guardrail_block_alucination.
```

(*) There is a Makefile with theses commands that you can use