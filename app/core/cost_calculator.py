
def calculate_ai_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculate estimated cost based on model name and token usage.
    Rates per 1M tokens (USD).
    """
    model = model_name.lower()
    
    # Default rates (GPT-4 8k Original)
    rate_input = 30.0
    rate_output = 60.0
    
    if "gpt-4o" in model:
        # GPT-4o ($5 / $15)
        rate_input = 5.0
        rate_output = 15.0
    elif "turbo" in model or "gpt-4.1" in model:
        # GPT-4 Turbo ($10 / $30) -> Mapping "gpt-4.1" here as requested
        rate_input = 10.0
        rate_output = 30.0
    elif "gpt-3.5" in model:
        # GPT-3.5 Turbo ($0.50 / $1.50)
        rate_input = 0.5
        rate_output = 1.5
        
    cost = (prompt_tokens * rate_input / 1_000_000) + (completion_tokens * rate_output / 1_000_000)
    return cost
