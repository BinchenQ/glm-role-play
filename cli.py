import itertools
import json
import pprint
from typing import Iterator, Optional
from dotenv import load_dotenv
load_dotenv()
import api
from api import *
from data_types import *



def transfer_message_role(messages: MsgList):
    for message in messages:
        if message["role"] == "user":
            message["role"] = "assistant"
        elif message["role"] == "assistant":
            message["role"] = "user"
    return messages



class Role:

    def __init__(self, name, description) -> None:
        self.name = name
        self.description = description

    
    def chat(self, messages: MsgList, meta: CharacterMeta) -> Iterator[str]:
        response =  get_characterglm_response_via_sdk(
            messages=messages,
            meta=meta
        )
        # 返回的是stream，打印
        print(f'{self.name}: {response}')
        return response
    

    def generate_role_appearance(self) -> Iterator[str]:
        """ 用chatglm生成角色的外貌描写 """
            
        instruction = f"""
        请从下列文本中，抽取人物的外貌描写。若文本中不包含外貌描写，请你推测人物的性别、年龄，并生成一段外貌描写。要求：
        1. 只生成外貌，服饰描写，不要生成任何多余的内容。
        2. 外貌描写不能包含敏感词，人物形象需得体。
        3. 尽量用短语描写，而不是完整的句子。
        4. 不要超过50字

        文本：
        {self.description}
        """
        return get_chatglm_response_via_sdk(
            messages=[
                {
                    "role": "user",
                    "content": instruction.strip()
                }
            ]
        )
    
    def generate_role_image(self):
        return api.generate_cogview_image(
            prompt=self.generate_role_appearance()
        )
    

def generate_roles(topic: str) -> str:
    """
    由glm随机生成两个角色
    """
    
    instrcution = f"""
    你是一个充满想象力并且知识渊博的作家，根据指定的主题，来生成2个角色人设。使用中文
    要求：
    1. 角色必须是人物，如果是虚拟的人物，请你设计符合主题的人设。
    2. 如果有原著，必须使用原著存在的角色
    3. 角色必须包含外表，性格，角色关系的描述，尽量使用短语
    5. 角色信息必须包含name和description, name和description内容都是字符串
    6. 格式要求：python3的list, 列表元素是字典, 不要包含任何其他前缀后缀或者无关的内容
    主题：
    {topic}
    """
    roles: str = get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instrcution.strip()
            }
        ]
    )
    print(f'已生成角色：{roles}')
    roles = json.loads(roles.lstrip("```python").rstrip("```"))
    return roles

# 根据角色列表生成问候语
def generate_greeting(roles: List[dict]) -> str:
    """
    根据角色描述生成初始的对话
    """
    
    instrcution = f"""
    你是一个充满想象力并且知识渊博的作家，现在有两个角色人设，他们即将进行一段对话，请你根据角色特点设计一句开场白。要求：
    1. 开场白应该符合人物的性格特点
    2. 总是第一个角色先说话，使用完整但简短的句子
    3. 当需要描述人物表情，神态，旁白等内容时，使用圆括号，例如（害羞）
    5. 只保留说话的内容，使用中文
    角色信息：
    {roles}
    """
    return get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instrcution.strip()
            }
        ]
    )

# 根据角色列表生成一段场景描述
def generate_scene(roles: List[dict]) -> str:
    """
    根据角色描述生成初始的对话
    """
    
    instrcution = f"""
    你是一个充满想象力并且知识渊博的作家，现在有两个角色人设，他们即将进行一段对话，他们可能是虚拟的也可能是实际存在的。要求：
    1. 为这段对话设计一个场景描述，如果是虚拟角色，请用虚拟角色的设定来描述场景，
    2. 如果角色是实际存在的，场景描述应该符合实际，例如 
    3. 描述场景时，请用一个句子
    4. 当需要描述人物表情，神态，旁白等内容时，可以使用圆括号，例如（害羞）
    5. 直接返回结果，不要添加多余的内容，不要超过100字，使用中文
    角色信息如下：
    {roles}
    """
    return get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instrcution.strip()
            }
        ]
    )
            
if __name__ == "__main__":
    # 剧情主题，可以根据剧情主题自动生成角色
    topic = "地铁上偶遇老同学"
    # 可以自己提前设置或根据主题自动生成
    default_role_list = []
    role_list = default_role_list if default_role_list else generate_roles(topic=topic)
    roles =  [Role(name=role["name"], description=role["description"]) for role in role_list]
    greeting =  generate_greeting(role_list)
    scene = generate_scene(role_list)
    print(f'{scene}')
    print("聊天开始...")
    print('-' * 100)
    print(greeting)
    # 对话总是从第一个角色开始
    speaker, listener = roles[0], roles[1]
    history = [
        {
            "role": "user",
            "content": f'({scene}) {greeting}'
        }
    ]
    # 控制对话长度
    for i in range(30):
        meta={
                "user_info": speaker.description,
                "bot_info": listener.description,
                "bot_name": listener.name,
                "user_name": speaker.name
        }
        response = listener.chat(
            messages=history,
            meta=meta
        )
        history.append({
            "role": "assistant",
            "content": response
        })
        history = transfer_message_role(history)
        speaker, listener = listener, speaker
        i += 1
    # print(speaker.generate_role_image())