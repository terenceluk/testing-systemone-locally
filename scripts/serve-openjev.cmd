@echo off
rem Downloads OpenJev on first run (about 28.6 GB at Q8_0, plus the mmproj file) and serves it on http://127.0.0.1:8080
rem Requires the llama command from https://llama.app/
rem Remove :Q8_0 to get the default Q4_K_M file, which is about 19 GB.
rem OpenJev's weights are licensed CC BY-NC 4.0, for non-commercial use only.
rem If you use a Hugging Face token, set it in your own session first with: set HF_TOKEN=your_token
llama serve -hf ggml-org/OpenJev-GGUF:Q8_0
