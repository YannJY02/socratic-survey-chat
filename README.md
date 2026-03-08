# Socratic Survey Chat

An open-source research platform for studying AI-assisted Socratic teaching in education.

The system pairs a locally-deployed open-source large language model with a web-based chat interface to conduct Socratic tutoring sessions. Participants complete a pre-test survey, interact with the AI tutor, and then complete a post-test survey. This design enables controlled measurement of learning outcomes.

## Architecture

The platform connects three components through URL-based participant tracking:

```
┌─────────────────┐     pid      ┌─────────────────┐     pid      ┌─────────────────┐
│                  │  ────────►   │                  │  ────────►   │                  │
│  Qualtrics       │              │  Streamlit       │              │  Qualtrics       │
│  Pre-Test Survey │              │  AI Chat (local) │              │  Post-Test Survey│
│                  │              │                  │              │                  │
└─────────────────┘              └────────┬─────────┘              └─────────────────┘
                                          │
                                          │ Ollama API
                                          ▼
                                 ┌─────────────────┐
                                 │  Phi-3-mini      │
                                 │  Socratic Model  │
                                 │  (local)         │
                                 └─────────────────┘
```

**Data flow:**

1. Participant starts the Qualtrics pre-test survey.
2. On survey completion, Qualtrics redirects to the Streamlit app with a `pid` (participant ID) in the URL.
3. The participant chats with the Socratic AI tutor. All messages are logged locally with the `pid`.
4. When the session ends, the app redirects to the Qualtrics post-test survey, passing the `pid`.
5. The researcher matches pre-test, chat logs, and post-test data using the shared `pid`.

## Quick Start

```bash
# 1. Install Ollama
brew install ollama

# 2. Download the Socratic model
ollama pull eurecom-ds/phi-3-mini-4k-socratic

# 3. Clone the project and enter the directory
cd socratic-survey-chat/

# 4. Run the setup script (creates venv, installs dependencies, copies .env)
chmod +x scripts/setup.sh
./scripts/setup.sh

# 5. Start the application
ollama serve &
streamlit run app.py
```

For detailed instructions, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md).

## Project Structure

```
socratic-survey-chat/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore rules
├── config.py                          # Application configuration
├── app.py                             # Streamlit chat application
├── logger.py                          # Conversation logging module
├── prompts/
│   └── socratic_tutor.txt             # System prompt for the Socratic tutor
├── scripts/
│   ├── setup.sh                       # Automated setup script
│   └── export_logs.py                 # Export chat logs to CSV for analysis
├── logs/                              # Chat session logs (git-ignored)
│   └── .gitkeep
├── data/                              # Exported data for analysis (git-ignored)
│   └── .gitkeep
├── tests/
│   └── test_app.py                    # Application tests
└── docs/
    ├── SETUP_GUIDE.md                 # Detailed setup instructions
    └── QUALTRICS_INTEGRATION.md       # Qualtrics survey integration guide
```

## Model Information

This project uses the [Phi-3-mini Socratic model](https://giovannigatti.github.io/socratic-llm/) developed by EURECOM, a 3.8 billion parameter model based on Microsoft's Phi-3-mini, fine-tuned with Direct Preference Optimization (DPO) for Socratic dialogue.

The model is designed to guide students toward answers through questioning rather than providing direct answers, following the Socratic teaching method.

- **Base model:** Microsoft Phi-3-mini-4k-instruct (3.8B parameters)
- **Fine-tuning method:** DPO (Direct Preference Optimization)
- **Context window:** 4,096 tokens
- **Model ID:** `eurecom-ds/phi-3-mini-4k-socratic`
- **Hardware requirements:** Runs on consumer hardware (tested on MacBook Pro M1 with 16GB RAM)

### Citation

```bibtex
@inproceedings{gatti2024socratic,
  title={Fine-Tuning LLMs for Socratic Tutoring: A Pipeline Using Synthetic Dialogues},
  author={Gatti, Giovanni and Gomez, Luca and Popescu, Marius},
  booktitle={Proceedings of the AIxEDU Workshop at ECAI 2024},
  series={CEUR Workshop Proceedings},
  volume={3879},
  year={2024}
}
```

## Ethics and Privacy

This platform is designed with research ethics and data privacy as core requirements:

- **Local-only model deployment:** The LLM runs entirely on the researcher's machine via Ollama. No conversation data is sent to external APIs or cloud services.
- **No third-party AI services:** Unlike platforms using OpenAI or similar APIs, all inference happens locally, ensuring participant conversations remain on-premises.
- **Participant pseudonymization:** Participants are identified only by a randomly generated `pid`. No personally identifiable information is stored in chat logs.
- **Data minimization:** Only the conversation content and timestamps are logged, alongside the participant ID.

These design choices support compliance with institutional ethics board requirements and GDPR obligations for research involving human participants.

## Tools and Technologies

| Component | Tool | Purpose |
|-----------|------|---------|
| LLM serving | [Ollama](https://ollama.com/) | Local model inference |
| Chat interface | [Streamlit](https://streamlit.io/) | Web-based chat UI |
| Surveys | [Qualtrics](https://www.qualtrics.com/) | Pre/post-test data collection |
| Model | [Phi-3-mini Socratic](https://giovannigatti.github.io/socratic-llm/) | Socratic tutoring LLM |

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE) (AGPL-3.0).
