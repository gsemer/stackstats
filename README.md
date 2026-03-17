# StackStats Service

A long-running REST API service that retrieves data from the StackExchange API, computes statistics over a given datetime range, and caches results in Redis.

---

## Table of Contents

- [Architecture](#architecture)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Running the Service](#running-the-service)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)

---

## Architecture

The service follows Domain-Driven Design architecture.

**Tech stack:**
- **FastAPI** — async REST framework with automatic OpenAPI docs
- **aiohttp** — async HTTP client for StackExchange API communication
- **Redis** — caching layer to serve repeated requests without hitting the API
- **Docker + docker-compose**

**Key design decisions:**
- All I/O is fully async (`asyncio` + `aiohttp`)
- A `Semaphore` limits concurrent outbound API requests to avoid rate limiting
- Retry logic with configurable attempts and wait time handles transient failures
- Comment fetching is batched in groups of 100 (StackExchange API limit)
- Results are cached in Redis with a configurable TTL; cache is checked before any API call

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/) + [docker-compose](https://docs.docker.com/compose/)

That's it. No local Python installation needed.

---

## Configuration

All settings are managed via environment variables:

| Variable                  | Default                              | Description                                      |
|---------------------------|--------------------------------------|--------------------------------------------------|
| `STACKEXCHANGE_KEY`       | *(empty)*                            | StackExchange API key |
| `STACKEXCHANGE_BASE_URL`  | `https://api.stackexchange.com/2.3`  | StackExchange API base URL                       |
| `STACKEXCHANGE_SITE`      | `stackoverflow`                      | Target StackExchange site                        |
| `REDIS_URL`               | `redis://stackexchange-redis:6379`                 | Redis connection URL                             |
| `TTL`                     | `3600`                               | Cache TTL in seconds                             |
| `PAGE_SIZE`               | `100`                                | Items per page for paginated API calls           |
| `MAX_CONCURRENCY`         | `5`                                  | Max concurrent outbound API requests             |
| `RETRY_ATTEMPTS`          | `3`                                  | Number of retry attempts on API failure          |
| `RETRY_WAIT`              | `2`                                  | Seconds to wait between retries                  |
| `REQUEST_TIMEOUT`         | `30`                                 | HTTP request timeout in seconds                  |

> **Note:** A StackExchange API key is optional but recommended. Without one, requests are limited to 300/day. Register an app at [stackapps.com](https://stackapps.com) to obtain a key (10,000 requests/day).

**How to set environment variables**

Create a `.env` file with the required variables (see above).

---

## Running the Service

### Start

```bash
docker build -t stackexchange .

docker-compose up -d
```

The service will be available at `http://localhost:5000`.

Interactive API docs (Swagger UI) are available at `http://localhost:5000/docs`.

### Stop

```bash
docker-compose down
```

### Stop and remove cached data

```bash
docker-compose down -v
```

---

## API Reference

### `GET /api/v1/stackstats`

Returns StackOverflow statistics for a given datetime range.

#### Query Parameters

| Parameter | Type   | Required | Format                | Description          |
|-----------|--------|----------|-----------------------|----------------------|
| `since`   | string | yes       | `YYYY-MM-DD HH:MM:SS` | Start of the range   |
| `until`   | string | yes       | `YYYY-MM-DD HH:MM:SS` | End of the range     |

#### Example Request

```bash
curl --request GET \
  --url "http://localhost:5000/api/v1/stackstats?since=2023-01-02%2010:00:00&until=2023-01-02%2011:00:00"
```

#### Example Response

```json
{
  "total_accepted_answers": 10,
  "accepted_answers_average_score": 23.8,
  "average_answers_per_question": 1.3,
  "top_ten_answers_comment_count": {
    "38149500": 1,
    "38152507": 7,
    "38147398": 5,
    "38142598": 2,
    "38149856": 0,
    "38143675": 3,
    "38143335": 1,
    "38143566": 0,
    "38143884": 9,
    "38143115": 1
  }
}
```

#### Response Fields

| Field                          | Type   | Description                                              |
|--------------------------------|--------|----------------------------------------------------------|
| `total_accepted_answers`       | int    | Number of accepted answers in the given range            |
| `accepted_answers_average_score` | float | Mean score of all accepted answers                     |
| `average_answers_per_question` | float  | Mean number of answers per unique question               |
| `top_ten_answers_comment_count`| object | Comment count for each of the 10 highest-scored answers  |

#### Error Responses

| Status | Condition                              |
|--------|----------------------------------------|
| `400`  | `since` is after `until`              |
| `422`  | Invalid datetime format in parameters  |

---

## Running Tests

Tests run inside Docker to ensure a consistent environment:

```bash
sudo docker exec -it stackexchange-app bash -c "python -B -m pytest"
```

---

## Project Structure

```
api/
├── dependencies.py           # FastAPI dependency injection
├── lifespan.py               # Startup/shutdown resource management
├── routes.py                 # Endpoint definitions
└── test_routes.py            # Test routes
application/
└── services/
    ├── calculator.py         # Statistics computation
    ├── stackexchange.py      # Orchestration + caching logic
    └── test_stackexchange.py # Test the service
domain/
├── exceptions.py             # Custom exceptions
├── interfaces.py             # Abstract base classes
└── models.py                 # Domain models (Answer, Comment)
infrastructure/
├── cache/
│   └── redis_cache.py        # Redis cache implementation
└── client/
    └── stackexchange.py      # StackExchange HTTP client
schemas/
└── response.py               # Pydantic response schemas
stackexchange/
└── settings.py               # App configuration via env vars
main.py                       # FastAPI app entry point
.env
docker-compose.yml
Dockerfile
requirements.txt
```