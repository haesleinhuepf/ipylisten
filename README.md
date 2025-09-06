# ipylisten

Dictate to Jupyter: activate the microphone, transcribe text into the current notebook cell.

## Installation

```bash
pip install ipylisten
```

## Usage

In a Jupyter notebook cell:

```python
from ipylisten import listen

# Start listening with default microphone
listen()
```

- The cell will print "listening..." while recording.
- After you stop speaking, your text is grammar-corrected by an LLM and written into the current cell.

### Environment
- Set `OPENAI_API_KEY` in your environment for the LLM.

### Optional parameters
```python
listen(microphone_index=None, timeout=10, model="gpt-5-mini")
```

