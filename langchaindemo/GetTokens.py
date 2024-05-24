import tiktoken
import cfg


## 使用`tiktoken.get_encoding()`按名称加载编码。第一次运行时，它将需要互联网连接进行下载。后续运行不需要互联网连接。
#encoding1 = tiktoken.get_encoding("cl100k_base")
## 使用`tiktoken.encoding_for_model()`函数可以自动加载给定模型名称的正确编码。
#encoding2 = tiktoken.encoding_for_model("gpt-3.5-turbo")
## encoding1和encoding2是等价的，因为gpt-3.5-turbo使用的编码名称是cl100k_base
#print(encoding1.encode("tiktoken is great!"))
#print(encoding2.encode("tiktoken is great!"))

# 初始化GPT-3的编码器
enc = tiktoken.get_encoding("cl100k_base")


# 计算 tokens 数量
tools_tokens = sum([len(enc.encode(str(tool))) for tool in cfg.tools])
system_prompt_tokens = sum([len(enc.encode(prompt["content"])) for prompt in cfg.SystemPrompt])
tool_prompt_tokens = len(enc.encode(cfg.ToolPrompt))

# 输出结果
print(tools_tokens, system_prompt_tokens, tool_prompt_tokens, tools_tokens + system_prompt_tokens + tool_prompt_tokens)
