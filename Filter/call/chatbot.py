import json

import system_prompt as sp
api_file_path = 'C:\\Users\\刘梦娇\\.config\\qwq'
with open(api_file_path, 'r') as f:
    api_key = f.readline().strip()

# import openai
from openai import OpenAI
# 初始化客户端
client = OpenAI(
    base_url="https://yunwu.ai/v1",
    api_key=api_key,
    timeout=120
)

model = "deepseek-r1-2025-01-20"


class ChatBot:

    def __init__(self, system_prompt=None, prompt_prefix=None, model="deepseek-r1-2025-01-20", temperature=0.1, max_tokens=4096):
        self.history = []
        self.model = model
        self.max_context = 10
        self.temperature = temperature
        self.max_tokens = max_tokens
        # 自定义
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = sp.system_prompt[model]
        self.system_prompt += "### User Inputs\n"
        if prompt_prefix:
            self.system_prompt += json.dumps(prompt_prefix, indent=4)
        # print(self.system_prompt)

    def chat(self, prompt, add_to_history=False, stream=False):
        prompts = [{"role": "system", "content": self.system_prompt}]
        context = ""

        for history in self.history:
            context += f"{history['question']}\n{history['answer']}\n"
            prompts.append({"role": "user", "content": history['question']})
            prompts.append({"role": "assistant", "content": history['answer']})
        # prompts.append({"role": "user", "content": context})
        prompts.append({"role": "user", "content": prompt})

        # # create a completion
        # response = openai.completions.create(model=self.model, prompt=prompt, max_tokens=64)
        # # print the completion
        # # print(prompt + completion.choices[0].text)

        # # create a chat completion
        if stream:
            stream_res = client.chat.completions.create(
                model=self.model,
                messages=prompts,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )
            res = ''
            for chunk in stream_res:
                if len(chunk.choices) == 0:
                    continue
                if chunk.choices[0].delta.content is not None:
                    res += chunk.choices[0].delta.content
        else:
            response = client.chat.completions.create(
                model=self.model,
                messages=prompts,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            # print the completion
            # print(completion.choices[0].message.content)
            res = response.choices[0].message.content

        if len(self.history) > self.max_context:
            # self.history.pop(0)
            # delete items from the end of the list
            self.history.pop()
        if add_to_history:
            self.history.append({"question": prompt, "answer": res if res is not None else "None"})
        return res

    def query(self, prompt):
        prompts = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": prompt}]

        # create a completion
        response = client.chat.completions.create(
            model=self.model,
            messages=prompts,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        # print the completion
        # print(prompt + completion.choices[0].text)

        res = response.choices[0].message.content
        return res


if __name__ == "__main__":
    #     text = """
    # import torch
    # arg_1_tensor = torch.rand([3, 2], dtype=torch.float64)
    # arg_1 = arg_1_tensor.clone()
    # res = torch.abs(arg_1,)

    # """
    #     chatbot = ChatBot(model)
    # chatbot.chat("public int maximumSwap(int num)
    # chatbot.chat("What is the equivalent function to `torch.abs` in tensorflow? "
    #              "If there is one equivalent function, directly give me the function name."
    #              "Otherwise, say No Equivalent Function.")

    chatbot = ChatBot()
    # prompt_file = '/data/yangchen/codamosa-llm/prompt_1015/ansible.cli.adhoc/prompt_0.txt'
    # with open(prompt_file, 'r') as f:
    #     prompt = f.read()

    prompt = """
    [Variables]
    ```
    str
    ```
    [DataFlows]
    ```
    [
      "ch = str.charAt(0)"
    ]
    ```
    [Constraints]
    ```
    [
      "!(str == \"true\")",
      "!(str == null)",
      "str.length() == 3",
      "!(ch == 'y')",
      "!(ch == 'Y')"
    ]
    ```
            """
    print(prompt)
    res = chatbot.query(prompt)
    print(res)



    # while True:
    #     print('User:')
    #     prompt = input()
    #     chatbot.chat(prompt, True)
    #
    #     # display(chatbot.history)
    #     for history in chatbot.history:
    #         print("Question:")
    #         print(history["question"])
    #         print("Answer:")
    #         print(history["answer"])
    #     print("----")
