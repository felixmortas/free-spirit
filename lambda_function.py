"""
/!\ TO ADJUST /!\ 

AWS Lambda Entry Point for ReAct Agent WhatsApp Chatbot
Handles WhatsApp webhook verification and incoming messages via the Cloud API.
"""

import os
import json
import logging

from agent import create_email_agent
from chat_session import ChatSession
from langfuse_engine import langfuse_handler

# ==================== LOGGING ====================

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ==================== AGENT INITIALISATION ====================
# Initialised once at cold start and reused across warm invocations.

MODEL_NAME = os.environ.get("MODEL_NAME", "mistral-small-latest")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

_agent = create_email_agent(model_name=MODEL_NAME, debug=DEBUG)

# ==================== WHATSAPP HELPERS ====================

def _verify_webhook(event: dict) -> dict:
    """
    Responds to Meta's webhook verification GET request.
    Expects WHATSAPP_VERIFY_TOKEN to be set as an environment variable.
    """
    params = event.get("queryStringParameters") or {}
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")

    if mode == "subscribe" and token == verify_token:
        logger.info("Webhook verified successfully.")
        return {"statusCode": 200, "body": challenge}

    logger.warning("Webhook verification failed. Token mismatch or wrong mode.")
    return {"statusCode": 403, "body": "Forbidden"}


def _extract_messages(body: dict) -> list[dict]:
    """
    Parses the WhatsApp Cloud API payload and returns a flat list of
    {"from": <phone_number>, "text": <message_text>} dicts.
    """
    messages = []
    try:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    if msg.get("type") == "text":
                        messages.append({
                            "from": msg["from"],
                            "text": msg["text"]["body"],
                            "message_id": msg.get("id"),
                        })
    except (KeyError, TypeError) as exc:
        logger.error("Failed to parse WhatsApp payload: %s", exc)
    return messages


def _send_whatsapp_reply(to: str, text: str) -> None:
    """
    Sends a reply via the WhatsApp Cloud API.
    Requires WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID env vars.
    """
    import urllib.request

    token     = os.environ["WHATSAPP_TOKEN"]
    phone_id  = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
    api_version = os.environ.get("WHATSAPP_API_VERSION", "v19.0")
    url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("WhatsApp reply sent to %s — status %s", to, resp.status)
    except Exception as exc:
        logger.error("Failed to send WhatsApp reply to %s: %s", to, exc)


# ==================== SESSION CACHE ====================
# Simple in-memory store keyed by sender phone number.
# Lives as long as the Lambda container stays warm.

_sessions: dict[str, ChatSession] = {}


def _get_session(phone: str) -> ChatSession:
    if phone not in _sessions:
        _sessions[phone] = ChatSession(agent=_agent, langfuse_handler=langfuse_handler)
        logger.info("New chat session created for %s", phone)
    return _sessions[phone]


# ==================== LAMBDA HANDLER ====================

def lambda_handler(event: dict, context) -> dict:
    """
    Main AWS Lambda entry point.

    Supports:
      - GET  → WhatsApp webhook verification challenge
      - POST → Incoming WhatsApp message processing
    """
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "POST")

    # ── Webhook verification ──────────────────────────────────────────────────
    if http_method == "GET":
        return _verify_webhook(event)

    # ── Incoming message ──────────────────────────────────────────────────────
    if http_method != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    # Parse body
    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON body received.")
        return {"statusCode": 400, "body": "Bad Request"}

    # WhatsApp sends a status-update ping with no messages — acknowledge quickly.
    messages = _extract_messages(body)
    if not messages:
        return {"statusCode": 200, "body": "OK"}

    # Process each message (typically just one per invocation)
    for msg in messages:
        sender = msg["from"]
        text   = msg["text"]
        logger.info("Message from %s: %s", sender, text)

        session = _get_session(sender)

        try:
            reply = session.send(text)
        except Exception as exc:
            logger.exception("Agent error for %s: %s", sender, exc)
            reply = "Sorry, something went wrong. Please try again in a moment."

        _send_whatsapp_reply(sender, reply)

    return {"statusCode": 200, "body": "OK"}