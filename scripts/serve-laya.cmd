@echo off
rem Downloads Laya on first run (449 MB at Q8_0) and serves it on http://127.0.0.1:8080
rem Requires the llama command from https://llama.app/
llama serve -hf ggml-org/Laya-GGUF
