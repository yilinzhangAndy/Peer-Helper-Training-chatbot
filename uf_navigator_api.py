# uf_navigator_api.py
import os
from typing import Optional, Tuple, Dict, Any

try:
    import streamlit as st
except Exception:
    st = None

from openai import OpenAI

# 延迟导入，避免循环依赖
try:
    from few_shot_examples import get_few_shot_examples, format_few_shot_prompt, FEW_SHOT_EXAMPLES
except ImportError:
    def get_few_shot_examples(*args, **kwargs):
        return []
    def format_few_shot_prompt(*args, **kwargs):
        return ""
    FEW_SHOT_EXAMPLES = {}


def _get_secret(name: str, default: str = "") -> str:
    """Prefer Streamlit secrets, then environment variables"""
    if st is not None:
        try:
            if name in st.secrets:
                return str(st.secrets.get(name, default))
        except Exception:
            pass
    return os.getenv(name, default)


# ---- Model fallback list (sentence generation) ----
UF_MODEL_FALLBACKS = [
    # 质量优先（更大更强但可能慢）
    "llama-3.3-70b-instruct",
    "llama-3.1-70b-instruct",
    "gemma-3-27b-it",
    # 速度/稳定性更好
    "mistral-small-3.1",
    "granite-3.3-8b-instruct",
    "llama-3.1-nemotron-nano-8B-v1",
]


def _is_retryable_model_error(e: Exception) -> bool:
    """判断是否是"可以尝试下一个模型"的错误（服务器端模型加载失败、模型不存在等）"""
    msg = str(e).lower()
    return (
        "cannot copy out of meta tensor" in msg
        or "meta tensor" in msg
        or "to_empty" in msg
        or "model not found" in msg
        or "unknown model" in msg
        or "invalid model" in msg
    )


class UFNavigatorAPI:
    """
    Wrapper for UF LiteLLM (OpenAI-compatible) endpoint.
    Required secrets (Streamlit Cloud -> App settings -> Secrets):
      - UF_LITELLM_BASE_URL
      - UF_LITELLM_API_KEY
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = (base_url or _get_secret("UF_LITELLM_BASE_URL") or "https://api.ai.it.ufl.edu").strip()
        self.api_key = (api_key or _get_secret("UF_LITELLM_API_KEY")).strip()  # ✅ 不允许硬编码默认 key

        self.last_error: str = ""
        self.client: Optional[OpenAI] = None

        if not self.api_key:
            self.last_error = (
                "❌ API key not provided. Please set UF_LITELLM_API_KEY in Streamlit secrets or env."
            )
            return
        if not self.base_url:
            self.last_error = (
                "❌ Base URL not provided. Please set UF_LITELLM_BASE_URL in Streamlit secrets or env."
            )
            return

        # Normalize base_url - 确保有 /v1 后缀
        self.base_url = self.base_url.rstrip("/")
        if not self.base_url.endswith("/v1"):
            self.base_url = self.base_url + "/v1"

        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout,
            )
        except Exception as e:
            self.last_error = f"Failed to create OpenAI client: {e}"
            self.client = None

    def test_connection(self) -> Tuple[bool, str]:
        """
        Minimal connectivity + auth check using models.list() (does NOT load models).
        This is safe to call during initialization as it doesn't trigger model loading.
        """
        if not self.client:
            return False, self.last_error or "Client not initialized."

        try:
            _ = self.client.models.list()
            return True, "OK"
        except Exception as e:
            msg = str(e)
            self.last_error = msg
            if "meta tensor" in msg.lower() or "torch" in msg.lower() or "cannot copy out of meta tensor" in msg.lower():
                return False, (
                    "⚠️ Server-side model loading error detected. "
                    "The UF LiteLLM API server is having trouble loading models. "
                    "This is a server-side issue, not a client-side problem. "
                    "Please try again later or contact UF IT support."
                )
            return False, msg
    
    def is_usable(self) -> bool:
        """
        Quick check if the API client is usable (client exists and credentials are set).
        This doesn't make any network calls, so it's safe to call frequently.
        """
        return self.client is not None and bool(self.api_key) and bool(self.base_url)

    def generate_chat(
        self,
        messages,
        model: str,
        max_tokens: int = 180,
        temperature: float = 0.8,
        top_p: float = 0.95,
    ) -> str:
        if not self.client:
            raise RuntimeError(self.last_error or "Client not initialized.")

        try:
            resp = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            # 捕获并重新抛出，让上层可以判断是否是可重试的错误
            error_msg = str(e)
            # 如果是 meta tensor 错误，这是一个可重试的服务器端错误
            if _is_retryable_model_error(e):
                # 创建一个带有特殊标记的异常，方便上层识别
                retryable_error = RuntimeError(f"Model loading error (retryable): {error_msg}")
                retryable_error.is_retryable = True
                raise retryable_error
            # 其他错误直接抛出
            raise

    def generate_student_reply(
        self,
        advisor_message: str,
        persona: str,
        knowledge_context: str = "",
        use_few_shot: bool = True,
        intent: Optional[str] = None,
        persona_info: Optional[Dict[str, Any]] = None,
        preferred_model: Optional[str] = None,
    ) -> Optional[str]:
        """
        Robust student reply generation with model fallback:
        - No hard-coded model
        - Try a few candidates; on "meta tensor"/torch error -> fall back to next model
        """
        if not self.client:
            self.last_error = self.last_error or "Client not initialized."
            return None

        import re

        # 1) Build prompt
        try:
            if use_few_shot:
                examples = get_few_shot_examples(
                    persona=persona,
                    advisor_message=advisor_message,
                    intent=intent,
                    num_examples=2,
                )

                persona_info = persona_info or {}

                conversation_context = None
                if "Previous conversation:" in advisor_message and "Now the advisor says:" in advisor_message:
                    conversation_context = (
                        advisor_message.split("Now the advisor says:")[0]
                        .replace("Previous conversation:", "")
                        .strip()
                    )

                prompt = format_few_shot_prompt(
                    examples=examples,
                    advisor_message=advisor_message,
                    persona=persona,
                    persona_info=persona_info,
                    conversation_context=conversation_context,
                    advisor_intent=intent,
                )

                if knowledge_context:
                    prompt = f"""Based on the following MAE professional knowledge:
{knowledge_context}

{prompt}"""
            else:
                prompt = f"""
You are a {persona} type student having a conversation with a peer advisor.

Peer Advisor said: {advisor_message}

Please generate a natural and authentic response based on the {persona} student characteristics.
Your response should be 1–3 sentences and conversational.

Response:
"""
                if knowledge_context:
                    prompt = f"""Based on the following MAE professional knowledge:
{knowledge_context}

{prompt}"""
        except Exception as e:
            self.last_error = f"Prompt build failed: {e}"
            return None

        # 2) Build messages
        sys_msg = {
            "role": "system",
            "content": (
                "You are a professional academic conversation assistant. "
                "Always respond in English. Generate natural, direct responses."
            ),
        }
        user_msg = {"role": "user", "content": prompt}

        # 3) ✅ 不要硬编码单一模型，改为"逐个尝试模型"
        # 如果指定了 preferred_model，优先尝试
        model_list = [preferred_model] if preferred_model else []
        model_list.extend([m for m in UF_MODEL_FALLBACKS if m != preferred_model])
        
        last_err = None

        for model_name in model_list:
            try:
                reply = self.generate_chat(
                    messages=[sys_msg, user_msg],
                    model=model_name,
                    max_tokens=250,
                    temperature=0.8,
                )

                reply = re.sub(r"<[^>]+>", "", reply).strip()
                if reply:
                    return reply

            except Exception as e:
                last_err = e
                error_msg = str(e)

                # ✅ 如果是可重试的模型错误（meta tensor、model not found 等）→ 换下一个模型继续试
                if _is_retryable_model_error(e):
                    # 静默记录，继续尝试下一个模型
                    print(f"⚠️ Model {model_name} failed with retryable error, trying next model...")
                    continue

                # 其他错误（比如 401/403/网络问题）→ 记录并返回 None，让上层走 fallback
                self.last_error = error_msg
                # 对于非重试错误，立即返回，不继续尝试其他模型
                print(f"❌ Non-retryable error with model {model_name}: {error_msg}")
                return None

        # 所有模型都失败
        if last_err:
            error_msg = str(last_err)
            # 如果是 meta tensor 错误，提供更友好的错误信息
            if _is_retryable_model_error(last_err):
                # 简化错误消息，避免过长
                self.last_error = f"Server-side model loading error (meta tensor): {error_msg[:200]}"
            else:
                self.last_error = f"All models failed. Last error: {error_msg[:200]}"
        else:
            self.last_error = "All models failed (no specific error)."
        
        # 只在调试模式下打印详细错误
        import os
        if os.getenv("DEBUG_UF_API", "").lower() == "true":
            print(f"❌ generate_student_reply failed after trying all {len(model_list)} models: {self.last_error}")
        return None
