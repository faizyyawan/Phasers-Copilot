# Deployment Plan

This file describes future deployment stages only. Do not create Docker configuration until you reach the deployment phase.

## Local Learning Environment

- Python virtual environment
- Local Qdrant mode or Qdrant container
- Local PostgreSQL
- Local Redis
- Hosted or local LLM

Use this stage to understand each component manually.

## Docker Compose Environment

Future services:

- FastAPI
- Next.js
- PostgreSQL
- Qdrant
- Redis
- Worker
- Optional model server

Use this stage after local components work individually.

## Staging

- Test data only
- Tracing enabled
- Evaluation runs before release
- Authentication configured
- Secret management configured
- Role-based access tested

## Production Considerations

- Database backups
- Qdrant snapshot strategy
- Monitoring and alerting
- Horizontal scaling
- Model serving capacity
- Data retention
- Incident response
- Audit logs
- Cost monitoring

