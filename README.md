# Team conflict detection

Usage instructions for the tool are described below under *Getting Started*.

## Introduction

The aim of this project is to reliably detect and mediate conflict in collaborative team settings.

The primary interface is a chat-like GUI where conversation transcripts can be provided and messages can be added to the conversation. On each received message, the application integrates the new message and the full conversation transcript with domain knowledge, instructions, previously collected questionnaire results, etc. to build an informed and relevant prompt, which is then sent to an LLM backend (currently ChatGPT). The response is displayed to the user in order to mediate the conflict if necessary.

## Getting started

### Install Docker Desktop

Follow the section [**Get Docker Desktop**](https://docs.docker.com/get-started/introduction/get-docker-desktop/) in the official Docker documentation to install Docker Desktop (if you don't have it installed yet).

### Clone the project

[Clone the repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository):
```bash
git clone git@github.com:hKerstholt/team-conflict-detection.git
```

Move into the project directory:
```bash
cd team-conflict-detection
```

### Add your API key

To make the API key available to the application, create a file called `.env` in the project directory and add the following line to it:
```
OPENAI_API_KEY=<Your OpenAI API key>
```

The Python package `openai` will look for an environment variable called `OPENAI_API_KEY`. If it exists, the application backend can use it to connect to the [OpenAI API](https://developers.openai.com/api/docs). If it does not exist, the `openai` package will complain that "the api_key client option must be set".

You can also run the Python code without Docker if you prefer. In this case, [save your API key as an environment variable](https://configu.com/blog/setting-env-variables-in-windows-linux-macos-beginners-guide/) called `OPENAI_API_KEY`.

### Run the application

If you are using Windows, start Docker Desktop so the Docker service is running.

Run the application with Docker Compose:
```bash
docker compose up
```

This will install all required dependencies and start the application.

Use Ctrl+C to stop the application again.

You can also choose to run it in the background with `docker compose up -d` and stop it again with `docker compose down`. View the console output with `docker compose logs backend` or `docker compose logs -f backend`.

If you want, you can watch the directory for changes and automatically restart the application if a file is changed. You can do this with `docker compose watch`.

### Visual Studio Code

You can run Docker Compose configuration files directly from Visual Studio Code with the official Docker extension. To do this, right click on `docker-compose.yml` and select **Compose Up**.

## Acknowledgements and attribution

This repository contains the software used for a research project for which a paper was submitted for publication at SMAP 2026. You are welcome to use or modify this project as needed. If you decide to do so, please cite our forthcoming paper.

Contributors to code:
* Heleen Kerstholt
* Angie Dong

Additional contributors to the paper: 
* Ioanna Lykourentzou
* Catarina M. Santos
* Isaac Alpizar-Chacon

## License

The code in this repository is published under the _Apache 2.0_ open source license, see `LICENSE`.
