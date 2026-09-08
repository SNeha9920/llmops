import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import AsyncOpenAI
from google import genai
from app.config import settings

client = AsyncOpenAI(api_key=settings.GEMINI_API_KEY)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    retry_error_callback=lambda retry_state: "Fallback: The AI service is currently experiencing high load. Please try again later."
)
async def generate_llm_response(prompt: str) -> tuple[str, int, float]:
    start_time = time.time()
    
    # Fallback / Mock behavior if API key is not configured
    if settings.GEMINI_API_KEY == "mock-key":
        latency = round(time.time() - start_time, 3)
        return f"Echo Response to: '{prompt}'", 42, latency

    # Initialize Gemini client
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Request completion using Gemini 2.5 Flash
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    latency = round(time.time() - start_time, 3)
    answer = response.text
    
    # Calculate token count from usage metadata if available
    tokens_used = 0
    if response.usage_metadata:
        tokens_used = (response.usage_metadata.prompt_token_count or 0) + (response.usage_metadata.candidates_token_count or 0)

    return answer, tokens_used, latency