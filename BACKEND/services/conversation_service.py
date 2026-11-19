
from datetime import datetime, timezone
from bson import ObjectId


# --------------------------------------------------
# 1. CREATE CONVERSATION
# --------------------------------------------------

async def create_conversation(
    db,
    user_id: str,
    mode: str,
    document_id: str | None = None,
    document_ids: list[str] | None = None
):
    if mode not in ["document", "global"]:
        raise ValueError("Invalid conversation mode")

    if mode == "document":
        if not document_id:
            raise ValueError("Document ID is required")
        document_ids = []

    elif mode == "global":
        document_id = None

        if not document_ids or len(document_ids) < 2:
            raise ValueError("Select at least two documents")

        document_ids = list(dict.fromkeys(document_ids))

        if len(document_ids) < 2:
            raise ValueError("Select at least two different documents")

    now = datetime.now(timezone.utc)

    conversation = {
        "user_id": user_id,
        "title": "New Chat",
        "mode": mode,
        "document_id": document_id,
        "document_ids": document_ids or [],
        "summary": "",
        "created_at": now,
        "updated_at": now
    }

    result = await db["conversations"].insert_one(conversation)

    conversation["_id"] = result.inserted_id

    return conversation


# --------------------------------------------------
# 2. GET SINGLE CONVERSATION
# --------------------------------------------------

async def get_conversation(
    db,
    conversation_id: str,
    user_id: str
):
    if not ObjectId.is_valid(conversation_id):
        raise ValueError("Invalid conversation ID")

    conversation = await db["conversations"].find_one({
        "_id": ObjectId(conversation_id),
        "user_id": user_id
    })

    if not conversation:
        raise ValueError("Conversation not found")

    return conversation


# --------------------------------------------------
# 3. GET ALL USER CONVERSATIONS
# --------------------------------------------------

async def get_user_conversations(
    db,
    user_id: str
):
    cursor = db["conversations"].find({
        "user_id": user_id
    }).sort("updated_at", -1)

    conversations = await cursor.to_list(length=100)

    for conversation in conversations:
        conversation["_id"] = str(conversation["_id"])

    return conversations


# --------------------------------------------------
# 4. GET CONVERSATION MESSAGES
# --------------------------------------------------

async def get_conversation_messages(
    db,
    conversation_id: str,
    user_id: str
):
    conversation = await get_conversation(
        db,
        conversation_id,
        user_id
    )

    cursor = db["chat_messages"].find({
        "conversation_id": conversation_id,
        "user_id": user_id
    }).sort("created_at", 1)

    messages = await cursor.to_list(length=500)

    for message in messages:
        message["_id"] = str(message["_id"])

    return {
        "conversation_id": conversation_id,
        "mode": conversation["mode"],
        "document_id": conversation.get("document_id"),
        "document_ids": conversation.get("document_ids", []),
        "messages": messages
    }


# --------------------------------------------------
# 5. DELETE CONVERSATION
# --------------------------------------------------

async def delete_conversation(
    db,
    conversation_id: str,
    user_id: str
):
    conversation = await get_conversation(
        db,
        conversation_id,
        user_id
    )

    await db["chat_messages"].delete_many({
        "conversation_id": conversation_id,
        "user_id": user_id
    })

    await db["conversations"].delete_one({
        "_id": conversation["_id"],
        "user_id": user_id
    })

    return {
        "message": "Conversation deleted successfully"
    }
