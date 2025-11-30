# Model Registry

**Legend:**

- **Speed**: ⚡ (Slow/High quality) | ⚡⚡ (Balanced) | ⚡⚡⚡ (Fast)
- **Quality**: ⭐⭐⭐ (Good) | ⭐⭐⭐⭐ (Better) | ⭐⭐⭐⭐⭐ (Best)
- **Cost**: /M = per million tokens
- **Status**: ✅ Installed | Available (can be installed/accessed)

| Model                               | Provider  | Context | Size/RAM      | Speed | Quality | Best For                      | Cost Input | Cost Output | Vision | Status      |
| ----------------------------------- | --------- | ------- | ------------- | ----- | ------- | ----------------------------- | ---------- | ----------- | ------ | ----------- |
| **LOCAL MODELS (20 models - FREE)** |           |         |               |       |         |                               |            |             |        |             |
| llama3.1:70b                        | Local     | 128K    | 42GB/64GB+    | ⚡     | ⭐⭐⭐⭐⭐   | High-end reasoning & analysis | $0         | $0          | ❌      | ✅ Installed |
| deepseek-r1:70b                     | Local     | 128K    | 42GB/64GB+    | ⚡     | ⭐⭐⭐⭐⭐   | Ultimate reasoning            | $0         | $0          | ❌      | ✅ Installed |
| codellama:34b                       | Local     | 100K    | 19GB/32GB+    | ⚡     | ⭐⭐⭐⭐⭐   | Best code quality             | $0         | $0          | ❌      | ✅ Installed |
| qwen2.5:32b                         | Local     | 128K    | 19GB/32GB+    | ⚡     | ⭐⭐⭐⭐⭐   | Premium intelligence          | $0         | $0          | ❌      | ✅ Installed |
| codellama:13b                       | Local     | 100K    | 7.4GB/16GB    | ⚡⚡    | ⭐⭐⭐⭐    | High-quality code             | $0         | $0          | ❌      | ✅ Installed |
| codellama:13b-code                  | Local     | 100K    | 7.4GB/16GB    | ⚡⚡    | ⭐⭐⭐⭐    | Code generation focus         | $0         | $0          | ❌      | ✅ Installed |
| qwen3:8b                            | Local     | 128K    | 5.2GB/12GB    | ⚡⚡    | ⭐⭐⭐⭐    | Multilingual reasoning        | $0         | $0          | ❌      | ✅ Installed |
| gemma:7b                            | Local     | 8K      | 5.0GB/8-12GB  | ⚡⚡    | ⭐⭐⭐⭐    | Google's balanced model       | $0         | $0          | ❌      | ✅ Installed |
| llama3.1:8b                         | Local     | 128K    | 4.9GB/8-12GB  | ⚡⚡    | ⭐⭐⭐     | General tasks                 | $0         | $0          | ❌      | ✅ Installed |
| llama3:8b                           | Local     | 8K      | 4.7GB/8-12GB  | ⚡⚡    | ⭐⭐⭐     | General conversations         | $0         | $0          | ❌      | ✅ Installed |
| qwen2.5:7b-instruct                 | Local     | 128K    | 4.7GB/8-12GB  | ⚡⚡    | ⭐⭐⭐⭐    | Instruction-tuned Qwen        | $0         | $0          | ❌      | ✅ Installed |
| magicoder:7b                        | Local     | 16K     | 3.8GB/8GB     | ⚡⚡    | ⭐⭐⭐⭐    | Optimal code balance          | $0         | $0          | ❌      | ✅ Installed |
| llama3.2:3b                         | Local     | 128K    | 2.0GB/4-6GB   | ⚡⚡⚡   | ⭐⭐⭐     | Fast conversations            | $0         | $0          | ❌      | ✅ Installed |
| deepseek-coder:1.3b                 | Local     | 16K     | 776MB/2-4GB   | ⚡⚡⚡   | ⭐⭐⭐     | Quick code snippets           | $0         | $0          | ❌      | ✅ Installed |
| llama3.2:90b                        | Local     | 128K    | ~90GB/128GB+  | ⚡     | ⭐⭐⭐⭐⭐   | Vision capable flagship       | $0         | $0          | ✅      | Available   |
| llama3.2:11b                        | Local     | 128K    | ~11GB/16GB    | ⚡⚡    | ⭐⭐⭐⭐    | Vision capable mid-size       | $0         | $0          | ✅      | Available   |
| llama3.1:405b                       | Local     | 128K    | ~240GB/256GB+ | ⚡     | ⭐⭐⭐⭐⭐   | Largest local model           | $0         | $0          | ❌      | Available   |
| llama3:70b                          | Local     | 8K      | ~40GB/64GB+   | ⚡     | ⭐⭐⭐⭐    | Previous gen high quality     | $0         | $0          | ❌      | Available   |
| **OPENAI MODELS (11 models)**       |           |         |               |       |         |                               |            |             |        |             |
| o1-pro                              | OpenAI    | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Ultimate reasoning            | $60/M      | $240/M      | ❌      | Available   |
| o1                                  | OpenAI    | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Deep reasoning                | $15/M      | $60/M       | ❌      | Available   |
| o1-mini                             | OpenAI    | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Balanced reasoning            | $3/M       | $12/M       | ❌      | Available   |
| gpt-4o                              | OpenAI    | 128K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Vision, balanced tasks        | $5/M       | $15/M       | ✅      | Available   |
| gpt-4-turbo                         | OpenAI    | 128K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Vision, function calling      | $10/M      | $30/M       | ✅      | Available   |
| gpt-4                               | OpenAI    | 8K      | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Complex reasoning             | $30/M      | $60/M       | ❌      | Available   |
| gpt-4o-mini                         | OpenAI    | 128K    | N/A           | ⚡⚡⚡   | ⭐⭐⭐     | Fast, cost-effective          | $0.15/M    | $0.6/M      | ✅      | Available   |
| gpt-3.5-turbo                       | OpenAI    | 16K     | N/A           | ⚡⚡⚡   | ⭐⭐⭐     | Quick tasks                   | $0.5/M     | $1.5/M      | ❌      | Available   |
| **ANTHROPIC MODELS (7 models)**     |           |         |               |       |         |                               |            |             |        |             |
| claude-opus-4.1                     | Anthropic | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Top reasoning                 | $20/M      | $100/M      | ✅      | Available   |
| claude-opus-4                       | Anthropic | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Premium Claude                | $15/M      | $75/M       | ✅      | Available   |
| claude-sonnet-4.5                   | Anthropic | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐⭐   | Latest balanced               | $4/M       | $20/M       | ✅      | Available   |
| claude-sonnet-4                     | Anthropic | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Balanced tasks                | $3/M       | $15/M       | ✅      | Available   |
| claude-3-opus                       | Anthropic | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Previous gen premium          | $15/M      | $75/M       | ✅      | Available   |
| claude-3.5-sonnet                   | Anthropic | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Popular balanced              | $3/M       | $15/M       | ✅      | Available   |
| claude-3-haiku                      | Anthropic | 200K    | N/A           | ⚡⚡⚡   | ⭐⭐⭐     | Fast, cost-effective          | $0.25/M    | $1.25/M     | ✅      | Available   |
| **BEDROCK MODELS (8 models)**       |           |         |               |       |         |                               |            |             |        |             |
| bedrock-claude-3-opus               | Bedrock   | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Premium reasoning             | $15/M      | $75/M       | ✅      | Available   |
| bedrock-claude-3.5-sonnet           | Bedrock   | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Balanced Claude               | $3/M       | $15/M       | ✅      | Available   |
| bedrock-llama-3.1-405b              | Bedrock   | 32K     | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Massive model power           | $5.32/M    | $16/M       | ❌      | Available   |
| bedrock-llama-3.1-70b               | Bedrock   | 32K     | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Strong reasoning              | $2.65/M    | $3.5/M      | ❌      | Available   |
| bedrock-titan-text-express          | Bedrock   | 8K      | N/A           | ⚡⚡⚡   | ⭐⭐⭐     | AWS native                    | $0.8/M     | $1.6/M      | ❌      | Available   |
| **GOOGLE GEMINI MODELS (6 models)** |           |         |               |       |         |                               |            |             |        |             |
| gemini-2.0-pro                      | Google    | 2M      | N/A           | ⚡⚡    | ⭐⭐⭐⭐⭐   | Research, analysis            | $1.5/M     | $6/M        | ✅      | Available   |
| gemini-2.0-flash                    | Google    | 1M      | N/A           | ⚡⚡⚡   | ⭐⭐⭐⭐    | Fast responses                | $0.1/M     | $0.4/M      | ✅      | Available   |
| gemini-1.5-pro                      | Google    | 2M      | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Previous gen pro              | $1.25/M    | $5/M        | ✅      | Available   |
| gemini-1.5-flash                    | Google    | 1M      | N/A           | ⚡⚡⚡   | ⭐⭐⭐     | Previous gen flash            | $0.075/M   | $0.3/M      | ✅      | Available   |
| **XAI GROK MODELS (5 models)**      |           |         |               |       |         |                               |            |             |        |             |
| grok-4-fast-reasoning               | xAI       | 2M      | N/A           | ⚡⚡    | ⭐⭐⭐⭐⭐   | Complex reasoning             | $2/M       | $6/M        | ❌      | Available   |
| grok-4-fast-non-reasoning           | xAI       | 2M      | N/A           | ⚡⚡⚡   | ⭐⭐⭐⭐    | Fast processing               | $1/M       | $3/M        | ❌      | Available   |
| grok-code-fast-1                    | xAI       | 256K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Code generation               | $1.5/M     | $4.5/M      | ❌      | Available   |
| grok-3                              | xAI       | 131K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | General tasks                 | $1/M       | $3/M        | ❌      | Available   |
| grok-2-vision-1212                  | xAI       | 32K     | N/A           | ⚡⚡    | ⭐⭐⭐     | Image analysis                | $2/M       | $6/M        | ✅      | Available   |
| **AZURE OPENAI MODELS (4 models)**  |           |         |               |       |         |                               |            |             |        |             |
| azure-gpt-4o                        | Azure     | 128K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Enterprise GPT-4o             | $5/M       | $15/M       | ✅      | Available   |
| azure-gpt-4-turbo                   | Azure     | 128K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Enterprise GPT-4 Turbo        | $10/M      | $30/M       | ✅      | Available   |
| azure-gpt-4                         | Azure     | 8K      | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Enterprise GPT-4              | $30/M      | $60/M       | ❌      | Available   |
| azure-claude-3.5-sonnet             | Azure     | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Enterprise Claude             | $3/M       | $15/M       | ✅      | Available   |
| **DIAL GATEWAY MODELS (2 models)**  |           |         |               |       |         |                               |            |             |        |             |
| dial-claude-opus-4                  | DIAL      | 200K    | N/A           | ⚡     | ⭐⭐⭐⭐⭐   | Enterprise access             | $15/M      | $75/M       | ✅      | Available   |
| dial-claude-sonnet-4                | DIAL      | 200K    | N/A           | ⚡⚡    | ⭐⭐⭐⭐    | Enterprise balanced           | $3/M       | $15/M       | ✅      | Available   |
