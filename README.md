# MeetPro Insights

## Introduction


## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

## Features

[List the key features of your project. This can include both functional and technical aspects.]

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/DAMG7374-Group9/AgentOPS_Assistant
   cd AgentOPS_Assistant
    ```


### Prerequisites

1. FFMPEG: Ensure you have FFmpeg installed on your system. You can download it from [FFmpeg's official website](https://www.ffmpeg.org/)
2. Python packages: Install the required Python packages using `poetry install --with frontend,backend`
3. Create a new file with the name `.env` and fill in the values using .env.template

### Steps to Run
1. **Backend**:
    ```sh
   uvicorn backend.main:app
    ```
2. **Frontend**:
    ```sh
    streamlit run app.py
    ```

