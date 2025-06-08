import openai
import os
import pandas as pd

# Initialize the new client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_df_for_prompt(df, sample_size=3):
    prompt_parts = []
    for col in df.columns:
        sample_vals = df[col].dropna().astype(str).sample(min(sample_size, len(df[col]))).tolist()
        sample_str = ", ".join(sample_vals)
        prompt_parts.append(f"{col}: {sample_str}")
    return "\n".join(prompt_parts)

def ask_llm_for_place_column(df):
    prompt_df = format_df_for_prompt(df)
    prompt = (
        "Below are columns from a dataframe with some sample data from each:\n\n"
        f"{prompt_df}\n\n"
        "Which column contains place names (e.g., Taco Bell, UT Austin Library, Starbucks)? "
        "Please reply only with the column name."
    )
    
    # Use chat completion with GPT-4 or GPT-3.5
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0,
        n=1,
        stop=None
    )
    answer = response.choices[0].message.content.strip()
    return answer

# Example usage
df = pd.DataFrame({
    "names": ["Taco Bell", "Starbucks", "UT Austin Library", "Chipotle"],
    "ids": [101, 102, 103, 104],
    "dates": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
})

place_col = ask_llm_for_place_column(df)
print("Column with place names:", place_col)

