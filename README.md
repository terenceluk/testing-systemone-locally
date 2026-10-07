# testing-systemone-locally

Scripts and two small browser games for testing open decision models through the `/v1/systemone` endpoint that llama.cpp added in October 2026.

A decision model does not generate text. You send it a `state` and one or more typed `questions`, and it returns a probability for each answer option in a single pass. This repo was built while testing two of them, Laya and OpenJev, on an HP ZBook Ultra G1a.

The write-up is on my blog: [LINK: blog post URL]

## What is in here

```text
testing-systemone-locally/
├── README.md
├── LICENSE
├── scripts/
│   ├── serve-laya.cmd         Start llama serve with Laya
│   ├── serve-openjev.cmd      Start llama serve with OpenJev
│   ├── send-request.ps1       Send one request with a choice, a noul, and a score question
│   └── time-requests.ps1      Time ten requests and print the fastest, median, and slowest
└── demos/
    ├── alert-invaders.html    Azure Monitor alerts fall, the model routes each one before it lands
    ├── space-invaders.html    Two boards side by side, you against the model
    └── prompt-eval.py         Scores different ways of wording the same question
```

## Requirements

- Windows, macOS, or Linux with the `llama` command installed from [llama.app](https://llama.app/). The `.cmd` and `.ps1` scripts are written for Windows.
- A build of llama.cpp that includes the `/v1/systemone` endpoint, which was merged on October 2, 2026.
- Python 3 for `prompt-eval.py`. It uses only the standard library.
- A browser for the two games. They are single HTML files with no dependencies and no build step.

## Quick start

Start a model. The first run downloads it into the Hugging Face cache.

```cmd
scripts\serve-laya.cmd
```

In a second window, send a request:

```powershell
.\scripts\send-request.ps1
```

Then time it:

```powershell
.\scripts\time-requests.ps1
```

Both PowerShell scripts accept `-Uri` if your server is not on `http://localhost:8080/v1/systemone`, and `time-requests.ps1` accepts `-Runs`.

## The two models

| | Laya | OpenJev |
|---|---|---|
| GGUF repository | [ggml-org/Laya-GGUF](https://huggingface.co/ggml-org/Laya-GGUF) | [ggml-org/OpenJev-GGUF](https://huggingface.co/ggml-org/OpenJev-GGUF) |
| Publisher | Convai Innovations | OpenJev, an independent project |
| Parameters | 0.4B | 26.9B |
| Download | 449 MB at Q8_0 | About 19 GB at Q4_K_M, 28.6 GB at Q8_0 |
| License of the weights | Apache 2.0 | CC BY-NC 4.0, non-commercial use only |

Neither model is TypeSafe AI's Jev, and OpenJev is not affiliated with TypeSafe. This repo contains no model weights. If you run OpenJev, its non-commercial license applies to your use of it.

## The games

Open either HTML file in a browser while `llama serve` is running, then press Start. Each page has a Mock mode that needs no server, and each remembers its settings between refreshes.

### Alert Invaders

Forty sample Azure Monitor alerts fall in ten waves that get faster. Each alert is sent to the model as one `choice` question across five queues, which are identity, network, compute, data, and cost. Every alert ends up in a column:

| Column | Meaning |
|---|---|
| One of the five queues, green | Routed to the right queue |
| One of the five queues, red | Routed to the wrong queue |
| Human review | The model answered with a confidence under the gate |
| Missed | The alert landed before the model answered |

Settings include the confidence gate, the number of parallel requests, and a game speed of 1x, 2x, 5x, or 10x. Pause and Stop are available during a run, and a per-wave results table appears at the end.

### Space Invaders

Two identical boards run side by side for a set number of seconds. You play the left one with the arrow keys and Space, and the model plays the right one. The model cannot see the screen, so the page describes the board in a sentence and sends it with each request. A panel under the model's board shows the sentence it was sent and the answer it gave.

The Prompt setting has two modes:

| Mode | What is sent |
|---|---|
| One fact, one question (default) | The page picks the one fact that matters and asks a four-option `choice` |
| Full description, two questions | The whole board in several sentences, with a `choice` for movement and a `noul` for firing |

The second mode is kept so the difference can be seen. In my testing Laya chose the sensible move 35% of the time with the full description and 100% of the time with one fact.

## prompt-eval.py

Builds 98 board situations, each with a known sensible move, and asks the loaded model the same question in eight wordings.

```cmd
python demos\prompt-eval.py
```

It prints the number correct, the average confidence for right and wrong answers, and how often each option was picked. It takes under a minute against Laya and about ten minutes against OpenJev.

The script calls `127.0.0.1` and not `localhost`, because on Windows Python tries IPv6 first and waits about two seconds on every request before falling back.

## Reading timings from the server console

`llama serve` does not print a duration for each request, but every line has a timestamp. For any task number, subtract the timestamp on its `slot launch_slot_` line from the timestamp on its `slot release` line to get the time the model spent on that decision.

## Notes

- The server listens on `127.0.0.1:8080` with no API key and accepts requests from any origin, which is why the HTML files can call it directly from disk. Do not expose it beyond your own machine in that state.
- The llama.cpp log says the default port will change to 9931 in a future release. Update the endpoint in the scripts and in each game when it does.
- Downloaded models live in the Hugging Face cache, at `%USERPROFILE%\.cache\huggingface\hub` on Windows and `~/.cache/huggingface/hub` on macOS and Linux.
