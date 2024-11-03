from openai import OpenAI
import json 
import gradio as gr 

def modify_config(service_name, key, value):
    msg = f"成功修改{service_name}服务参数: {key}:{value}"
    print(f"函数输出：{msg}")
    return json.dumps({"result": True, "message": msg})

def restart_service(service_name):
    msg = f'成功重启{service_name}服务'
    print(f"函数输出：{msg}")
    return json.dumps({"result": True, "message": msg})


def apply_manifest(resource_type, image):
    msg = f"成功切换{resource_type}, 镜像：{image}"
    print(f"函数输出：{msg}")
    return json.dumps({"result": True, "message": msg})

tools = [
    {
        "type": "function",
        "function": {
            "name": "modify_config",
            "description": "修改服务的配置",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": '需要修改的服务名称，例如：{service_name="loki"}',
                    },
                    "key": {
                        "type": "string",
                        "description": '需要修改的配置值参数的key，例如：{key="deleteTime"}',
                    },
                    "value": {
                        "type": "string",
                        "description": '需要修改的配置值参数的key所对应的值，例如：{value="5s"}',
                    },
                },
            },
            "required": ["service_name", "key", "value"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_service",
            "description": "重启服务",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": '需要重启的服务名称，例如：{service_name="loki"}',
                    },
                },
            },
            "required": ["service_name"]
        }
    },{
        "type": "function",
        "function": {
            "name": "apply_manifest",
            "description": "更新服务的镜像版本",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": '需要更新的服务名称，例如：{service_name="grafana"}',
                    },
                    "image": {
                        "type": "string",
                        "description": '需要更新的服务的镜像版本，例如：{image="grafana:v0.0.7"}',
                    }
                },
            },
            "required": ["service_name", "image"]
        }
    }
]

client = OpenAI(api_key="sk-cf4640fe1a604067a9e0d80feda8cf3e", base_url="https://api.deepseek.com/v1")

def chat(message, history):
    try:
        # 将对话历史转换为 OpenAI API 所需的格式
        history_openai_format = []
        history_openai_format.append({"role": "system", "content": "你需要需要按照用户的输入，选择合适的方法进行调用"})
        for human, ai in history:
            history_openai_format.append({"role": "user", "content": human})
            history_openai_format.append({"role": "assistant", "content": ai})
        history_openai_format.append({"role": "user", "content": message})
        
        try:
            # 调用 DeepSeek API 创建聊天完成
            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=history_openai_format,
                tools=tools,
                tool_choice="auto",
            )

            response_massage = response.choices[0].message
            tool_call = response_massage.tool
            
            partial_message = ""
            if tool_call is None:
                print("not tool_calls")
            else:
                available_functions = {
                    "restart_service": restart_service,
                    "apply_manifest": apply_manifest,
                    "modify_config": modify_config,
                }
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                partial_message.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                yield partial_message
                response = client.chat.completions.create(
                    model='deepseek-chat',
                    messages=history_openai_format,
                    temperature=1.0,
                    stream=True,
                )
            # for chunk in response:
            #     # 逐步构建并 yield 部分响应
            #     if chunk.choices[0].delta.content is not None:
            #         partial_message += chunk.choices[0].delta.content
            #         yield partial_message
        except Exception as api_error:
            # 处理 API 调用过程中的错误
            yield f"API Error: {str(api_error)}"
    except Exception as format_error:
        # 处理格式化历史记录时的错误
        yield f"Format Error: {str(format_error)}"

# 创建 Gradio 界面
iface = gr.ChatInterface(
    chat,
    chatbot=gr.Chatbot(height=500),
    title="Function Calling",
    description="Function Calling Demo.",
    theme="soft",
    examples=["Hello, how are you?", "What's the weather like today?"],
)

iface.launch()
