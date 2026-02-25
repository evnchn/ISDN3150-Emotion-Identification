# Docker Guide for ISDN3150 Emotion Identification

## About the Application

This is a NiceGUI web application that performs emotion analysis on text input. It uses Azure OpenAI (GPT-3.5 Turbo) with function calling to detect emotions such as happiness, sadness, anger, surprise, disgust, fear, and indifference from user-provided text. Results are displayed as color-coded cards with keywords, reasoning, and confidence scores.

## Prerequisites

You need an **Azure OpenAI API key** with access to the HKUST Azure endpoint (`https://hkust.azure-api.net`). The application will not function without a valid API key.

## Building the Docker Image

```bash
docker build -t kanjo-web .
```

## Running the Container

Basic usage (API key entered via the web UI):

```bash
docker run -p 8080:8080 kanjo-web
```

With the `OPENAI_API_KEY` environment variable (enables the `/admin` page with a pre-filled API key):

```bash
docker run -p 8080:8080 -e OPENAI_API_KEY=your-api-key-here kanjo-web
```

The application will be available at `http://localhost:8080`.

## Environment Variables

| Variable         | Required | Description                                                                 |
|------------------|----------|-----------------------------------------------------------------------------|
| `OPENAI_API_KEY` | No       | Azure OpenAI API key. If set, the `/admin` page will have the key pre-filled. Users can also enter their API key directly on the main page (`/`). |

## Port Mapping

The NiceGUI application listens on port **8080** inside the container. Map it to any host port you prefer:

```bash
docker run -p <host-port>:8080 kanjo-web
```

For example, to access the app on port 3000:

```bash
docker run -p 3000:8080 kanjo-web
```
