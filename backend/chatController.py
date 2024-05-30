from loguru import logger
from openai import OpenAI
import tiktoken

class ChatController(object):
    """docstring for ChatController"""

    def start_request(self):
        logger.info("Chat start request!")
        self.reduce_context()
        req = self.client.chat.completions.create(
            model=self.LANGUAGE_MODEL,
            messages=self.context
        )
        print(req.choices[0].message.content)
        ai_answer = req.choices[0].message.content
        ai_role = req.choices[0].message.role
        logger.debug("Full response:\n{}", str(req))
        self.join_context(ai_role, ai_answer, self.AI_NAME)
        logger.success("Chat started!")
        return ai_answer

    def answer_request(self, user_message, user_name=""):
        logger.info("Chat answer request!")
        self.join_context("user", user_message, user_name)
        self.reduce_context()
        req = self.client.chat.completions.create(
            model=self.LANGUAGE_MODEL,
            messages=self.context
        )
        ai_answer = req.choices[0].message.content
        ai_role = req.choices[0].message.role
        logger.debug("Full response:\n{}", str(req))
        self.join_context(ai_role, ai_answer, self.AI_NAME)
        logger.success("Chat answered!")
        return ai_answer

    def join_context(self, role, message, name=""):
        logger.info("Context update triggered!")
        if name == "":
            context_update = {"role": role, "content": message}
        else:
            context_update = {"role": role, "name": name, "content": message}
        logger.debug("Context update: \'{}\'", context_update)
        self.context.append(context_update)
        logger.debug("New context: \'{}\'", self.context)
        logger.success("Context updated!")

    def token_counter(self):  # Not precise, but close enough. Modified from OpenAI documentation
        try:
            encoding = tiktoken.encoding_for_model(self.LANGUAGE_MODEL)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = 0
        for message in self.context:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def reduce_context(self, max_tokens=3585):  # Maximum comes from the maximum tokens allowed (4096) minus 512
        logger.info("Verifying the use of tokens and reducing the context if needed...")
        current_tokens = self.token_counter()
        while current_tokens > max_tokens:
            logger.debug("Context is outside the correct parameters (Currently {} of a maximum of {}). Reducing...",
                         current_tokens, max_tokens)
            self.context.pop(1)  # Ignore the first element as it is the system instruction
            logger.debug("Context has been reduced, checking...")
            current_tokens = self.token_counter()
        logger.debug("Context is within the correct parameters (Currently {} of a maximum of {}).",
                     current_tokens, max_tokens)
        logger.success("Context reduced (if needed)!")

    def __init__(self, openai_api_key, personality, ai_name="", language_model="gpt-3.5-turbo"):
        super(ChatController, self).__init__()
        self.LANGUAGE_MODEL = language_model
        self.PERSONALITY = personality
        self.AI_NAME = ai_name
        self.context = [
            {"role": "system", "content": self.PERSONALITY}
        ]

        self.client = OpenAI(api_key=openai_api_key)

        logger.log("SETUP", "Model: {}", self.LANGUAGE_MODEL)
        if self.LANGUAGE_MODEL != "gpt-3.5-turbo":
            logger.warning("Current selected model is not stable!")
        logger.log("SETUP", "PERSONALITY: {}", self.PERSONALITY)
        if self.AI_NAME == "":
            logger.log("SETUP", "AI NAME: {}", self.AI_NAME)
            logger.log("WARNING", "AI NAME has not been set. Ignoring...")


class ChatControllerAsync(object):
    """docstring for ChatControllerAsync"""

    async def start_request(self):
        logger.info("Chat start request!")
        self.reduce_context()
        req = self.client.chat.completions.create(
            model=self.LANGUAGE_MODEL,
            messages=self.context
        )
        print(req.choices[0].message.content)
        ai_answer = req.choices[0].message.content
        ai_role = req.choices[0].message.role
        logger.debug("Full response:\n{}", str(req))
        self.join_context(ai_role, ai_answer, self.AI_NAME)
        logger.success("Chat started!")
        return ai_answer

    async def answer_request(self, user_message, user_name=""):
        logger.info("Chat answer request!")
        self.join_context("user", user_message, user_name)
        self.reduce_context()
        req = self.client.chat.completions.create(
            model=self.LANGUAGE_MODEL,
            messages=self.context
        )
        ai_answer = req.choices[0].message.content
        ai_role = req.choices[0].message.role
        logger.debug("Full response:\n{}", str(req))
        self.join_context(ai_role, ai_answer, self.AI_NAME)
        logger.success("Chat answered!")
        return ai_answer

    def join_context(self, role, message, name=""):
        logger.info("Context update triggered!")
        if name == "":
            context_update = {"role": role, "content": message}
        else:
            context_update = {"role": role, "name": name, "content": message}
        logger.debug("Context update: \'{}\'", context_update)
        self.context.append(context_update)
        logger.debug("New context: \'{}\'", self.context)
        logger.success("Context updated!")

    def token_counter(self):  # Not precise, but close enough. Modified from OpenAI documentation
        try:
            encoding = tiktoken.encoding_for_model(self.LANGUAGE_MODEL)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = 0
        for message in self.context:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def reduce_context(self, max_tokens=3585):  # Maximum comes from the maximum tokens allowed (4096) minus 512
        logger.info("Verifying the use of tokens and reducing the context if needed...")
        current_tokens = self.token_counter()
        while current_tokens > max_tokens:
            logger.debug("Context is outside the correct parameters (Currently {} of a maximum of {}). Reducing...",
                         current_tokens, max_tokens)
            self.context.pop(1)  # Ignore the first element as it is the system instruction
            logger.debug("Context has been reduced, checking...")
            current_tokens = self.token_counter()
        logger.debug("Context is within the correct parameters (Currently {} of a maximum of {}).",
                     current_tokens, max_tokens)
        logger.success("Context reduced (if needed)!")

    def message_intent_recognition(self, message):
        return self.client.embeddings.create(input=message, model="text-embedding-3-small")

    def __init__(self, openai_api_key, personality, ai_name="", language_model="gpt-3.5-turbo",
                 intent_recognition_is_enabled=False):
        super(ChatControllerAsync, self).__init__()
        self.LANGUAGE_MODEL = language_model
        self.PERSONALITY = personality
        self.AI_NAME = ai_name
        self.context = [
            {"role": "system", "content": self.PERSONALITY}
        ]
        self.intent_recognition_is_enabled = intent_recognition_is_enabled

        self.client = OpenAI(api_key=openai_api_key)

        logger.log("SETUP", "Model: {}", self.LANGUAGE_MODEL)
        if self.LANGUAGE_MODEL != "gpt-3.5-turbo":
            logger.warning("Current selected model is not stable!")
        logger.log("SETUP", "PERSONALITY: {}", self.PERSONALITY)
        if self.AI_NAME == "":
            logger.log("SETUP", "AI NAME: {}", self.AI_NAME)
            logger.log("WARNING", "AI NAME has not been set. Ignoring...")
