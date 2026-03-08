# Setup Guide

Step-by-step instructions for setting up the Socratic AI Tutor platform on your local machine.

## Prerequisites

- **macOS** (tested on MacBook Pro M1, 16GB RAM)
- **Python 3.9 or higher**
- **Approximately 10GB free disk space** (for the model weights and Python environment)
- **Homebrew** (recommended for installing Ollama)

Verify your Python version:

```bash
python3 --version
```

## Step 1: Install Ollama

Ollama is the local model server that runs the Socratic LLM on your machine.

**Option A: Install via Homebrew (recommended)**

```bash
brew install ollama
```

**Option B: Download from the website**

Download the macOS installer from [ollama.com/download](https://ollama.com/download) and follow the installation prompts.

After installation, verify Ollama is available:

```bash
ollama --version
```

## Step 2: Download the Socratic Model

Pull the fine-tuned Phi-3-mini Socratic model. This download is approximately 2.3GB.

```bash
ollama pull eurecom-ds/phi-3-mini-4k-socratic
```

Verify the model is available:

```bash
ollama list
```

You should see `eurecom-ds/phi-3-mini-4k-socratic` in the output.

**Optional: Test the model directly**

```bash
ollama run eurecom-ds/phi-3-mini-4k-socratic "What is photosynthesis?"
```

The model should respond with guiding questions rather than a direct answer, demonstrating its Socratic behavior.

## Step 3: Get the Project Files

If you received the project as a zip file, extract it and navigate to the `code/` directory.

If cloning from a repository:

```bash
git clone <repository-url>
cd socratic-survey-chat/
```

## Step 4: Run the Setup Script

The setup script automates virtual environment creation, dependency installation, and environment file configuration.

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The script will:
1. Create a Python virtual environment in `.venv/`
2. Install all dependencies from `requirements.txt`
3. Copy `.env.example` to `.env` if it does not already exist

If you prefer to set up manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Step 5: Configure the Application

Edit the `.env` file with your Qualtrics survey URLs:

```bash
nano .env
```

Set the following values:

```
OLLAMA_MODEL=eurecom-ds/phi-3-mini-4k-socratic
OLLAMA_BASE_URL=http://localhost:11434
POST_SURVEY_URL=https://your-university.qualtrics.com/jfe/form/SV_XXXXXXXXXX
```

Replace the `POST_SURVEY_URL` with your actual Qualtrics post-test survey URL. See [QUALTRICS_INTEGRATION.md](QUALTRICS_INTEGRATION.md) for details on setting up the survey flow.

You can also adjust settings in `config.py` if needed (e.g., model parameters, logging options).

## Step 6: Test the Application

Start the Ollama server (if it is not already running):

```bash
ollama serve
```

In a separate terminal, activate the virtual environment and launch the app:

```bash
source .venv/bin/activate
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

To test with a participant ID (simulating the Qualtrics redirect):

```
http://localhost:8501/?pid=TEST001
```

Verify that:
- The chat interface loads without errors
- You can send a message and receive a Socratic response
- The conversation is logged in the `logs/` directory
- The session end redirects to your post-test survey URL with the `pid` parameter

## Troubleshooting

### Ollama is not running

**Symptom:** The app shows a connection error or "Cannot connect to Ollama."

**Fix:** Start the Ollama server in a separate terminal:

```bash
ollama serve
```

On macOS, if you installed Ollama via the desktop app, it may run as a background service automatically. Check with:

```bash
curl http://localhost:11434/api/tags
```

If you get a JSON response, Ollama is running.

### Port 8501 is already in use

**Symptom:** Streamlit fails to start with a port conflict error.

**Fix:** Either stop the other process using port 8501, or run Streamlit on a different port:

```bash
streamlit run app.py --server.port 8502
```

### Out of memory errors

**Symptom:** The model loads slowly, crashes, or the system becomes unresponsive.

The Phi-3-mini model requires approximately 4GB of RAM for inference. On a MacBook Pro M1 with 16GB RAM, this should work comfortably, but issues can arise if many other applications are open.

**Fix:**
- Close unnecessary applications to free memory
- Monitor memory usage with Activity Monitor
- Restart Ollama: stop the server and run `ollama serve` again

### Model not found

**Symptom:** Error message indicating the model cannot be found.

**Fix:** Verify the model is downloaded:

```bash
ollama list
```

If the model is not listed, pull it again:

```bash
ollama pull eurecom-ds/phi-3-mini-4k-socratic
```

Ensure the model name in your `.env` file matches exactly: `eurecom-ds/phi-3-mini-4k-socratic`

### Virtual environment issues

**Symptom:** `ModuleNotFoundError` when running the app.

**Fix:** Make sure the virtual environment is activated:

```bash
source .venv/bin/activate
```

Your terminal prompt should show `(.venv)` at the beginning. Then reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Deploying on HPC Clusters

For experiments requiring more compute power or longer-running sessions, the application can be deployed on an HPC (High-Performance Computing) cluster with GPU support.

### Overview of Steps

1. **Request access:** Apply for a compute allocation through your institution's HPC service.
2. **Connect:** SSH into the cluster (`ssh username@your-cluster.example.com`).
3. **Install Ollama:** Download the Linux binary for Ollama on the compute node.
4. **Transfer project files:** Use `scp` or `rsync` to copy the project to your cluster home directory.
5. **Submit a job:** Write a SLURM batch script requesting a GPU node and run the setup and application within the job.
6. **Port forwarding:** Use SSH tunneling to access the Streamlit interface from your local browser:
   ```bash
   ssh -L 8501:localhost:8501 username@your-cluster.example.com
   ```
7. **Update Qualtrics redirect URLs** to point to the tunneled address or a publicly accessible endpoint if configured.

Consult your institution's HPC documentation and your supervisor for cluster-specific configuration.
