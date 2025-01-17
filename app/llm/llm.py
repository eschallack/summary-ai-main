# Main llm functionality
from enum import Enum, IntEnum
from app.llm import llm_utils
import ollama
import json
from pydantic import BaseModel, model_validator, Field
from pydantic import ValidationError
from typing import List, Dict, Union, Optional
from collections.abc import Callable

class LLM():
    def __init__(self):
        self.client = ollama.Client()
        self.messages = []
    def validate_json(self, text:str, failure_callback:Callable):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return failure_callback()
        
    def generate_chat(self, model:str="llama3.2:latest", temperature=1):
        response = self.client.chat(
            model='llama3.2:latest',
            messages=self.messages
        )
        return response['message']['content']
    def generate_chat_format(self,model_format:BaseModel, model:str="llama3.2:latest", temperature=.5, attempts=0):
        response = self.client.chat(
            model='llama3.2:latest',
            messages=self.messages,
            format=model_format.model_json_schema()
        )
        try:
            return model_format.model_validate_json(response['message']['content'])
        except ValidationError:
            attempts+=1
            if attempts == 10:
                return response['message']['content']
            print(f"Failed to validate response from chat format on attempt {str(attempts)}. {response['message']['content']}. Retrying...")
            return self.generate_chat(model_format, model=model, temperature=temperature, attempts=attempts)
    def generate_quality_control_check(self, old_text:str, new_text:str):
        class QualityControl(BaseModel):
            qc_pass:bool
            reason:str
        chat, system = llm_utils.load_local_yaml_prompt('app/prompts/quality_controller.yaml')
        chat = chat.replace("<<TEXT>>", old_text)
        chat = chat.replace("<<MODIFIED_TEXT>>", new_text)
        self.messages.extend([{'role':'system', 'content':system}, {'role':'user', 'content':chat}])
        res:QualityControl = self.generate_chat_format(QualityControl)
        return res
            
    def generate_short_synopsis(self, synopsis:str, context:Optional[dict[str,str]]="", max_length=80):
        if isinstance(context, dict):
            try:
                context = llm_utils.create_context(context)
            except:
                context = ""
        class ShortSynopsisModel(BaseModel):
            short_synopsis: str = Field(None, max_length=max_length, min_length=max_length//2)
        chat, system = llm_utils.load_local_yaml_prompt('app/prompts/text_shortener.yaml')
        chat = chat.replace("<<TEXT>>", synopsis)
        chat = chat.replace("<<CONTEXT>>", context)
        self.messages = [{'role':'system', 'content':system}, {'role':'user', 'content':chat}]
        return self.generate_chat()
    def generate_with_qc_pass(self, old_text:str, context:Optional[dict[str,str]]="", max_length=80, num_passes=10, pass_count=0):
        
        new_text = self.generate_short_synopsis(old_text, context, max_length=max_length)
        if len(new_text)>max_length:
            pass_count+=1
            print(f"""Attempt {str(pass_count)} failed AI Quality Control: 
                    Generated synopsis: {new_text}
                    Reason for failure: {len(new_text)} is too long""")
            return self.generate_with_qc_pass(new_text, context=f"The last attempt was TOO LONG!! Make it WAY shorter!", 
                                              max_length=max_length, 
                                              num_passes=num_passes,
                                              pass_count=pass_count)
        qc = self.generate_quality_control_check(old_text, new_text)
        if not qc.qc_pass:
            pass_count+=1
            print(f"""Attempt {str(pass_count)} failed AI Quality Control: 
                    Generated synopsis: {new_text}
                    Reason for failure: {qc.reason}""")
            if pass_count < num_passes:
                return self.generate_with_qc_pass(old_text, context=f"The last attempt failed for the following reason: {qc.reason}", 
                                              max_length=max_length, 
                                              num_passes=num_passes,
                                              pass_count=pass_count)
        print(f"""Attempt {str(pass_count)} PASSED AI Quality Control: 
                    Generated synopsis: {new_text}
                    Reason for Success: {qc.reason}""")
        return new_text, pass_count
    