from langchain.chat_models import ChatOllama
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
from langchain.output_parsers import OutputFixingParser
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain.chat_models import ChatOllama
from llmConstants import chat
# chat = ChatOllama(model='llama2', temperature=0)
import os 

os.environ['LANGCHAIN_TRACING'] = 'false'

# from langchain.llms import Ollama
# llm = Ollama(temperature=0)

from llmConstants import llm
# from langchain.chat_models import ChatOpenAI
# chat = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')

system_template = '''
Use the following pieces of context to answer the question.
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Use three sentences maximum and keep the answer as concise as possible.
'''
system_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template = '''
Context:
    Title: {title}
    Abstract: {abstract}

Question: {question}\n
{format_instructions}
'''
human_prompt = HumanMessagePromptTemplate.from_template(human_template)

response_schemas = [
  ResponseSchema(name="answer", description="a Yes or No answer", type="string"),
  ResponseSchema(name="explanation", description="Explanation on why it is or it isn't relevant", type="string")
]
excel_parser = StructuredOutputParser.from_response_schemas(response_schemas)

chat_prompt = ChatPromptTemplate(
    messages=[system_prompt, human_prompt], 
    partial_variables={
        "format_instructions":excel_parser.get_format_instructions(),
    }
)

output_fixer = OutputFixingParser.from_llm(parser=excel_parser, llm=llm)

retry_message = """
[INST]
  <<SYS>>
  The output has format JSONDecodeError preventing it from being parsed into a json object. Please help to correct it.
  Error: 
  {error}
  Current Output:
  {output}
  <</SYS>>
[/INST]
"""
retry_prompt = PromptTemplate.from_template(retry_message)