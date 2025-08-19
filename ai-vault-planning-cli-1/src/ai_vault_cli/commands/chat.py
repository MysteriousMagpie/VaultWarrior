from ai_vault_cli.llm.prompts import get_chat_prompt
from ai_vault_cli.utils.logging import logger
from ai_vault_cli.errors import ChatError

def chat(slug, message, write=False):
    try:
        prompt = get_chat_prompt(slug, message)
        response = call_openai_api(prompt)  # Assuming this function is defined elsewhere
        logger.info(f"Chat response for '{slug}': {response}")

        if write:
            append_to_thread(slug, response)  # Assuming this function is defined elsewhere
            logger.info(f"Appended response to thread '{slug}'")

        return response
    except Exception as e:
        logger.error(f"Error during chat: {str(e)}")
        raise ChatError("An error occurred while processing the chat.") from e