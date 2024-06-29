import pandas as pd
import openai
import datetime
import logging
openai.api_key = 'sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = f'logs{current_date}.txt'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s: %(message)s')

file_path = 'Review_text_data.xlsx'
review_data = pd.read_excel(file_path)
def call_assistant(review, prompt_type):
    if prompt_type == 1:  # Original detailed prompt
        messages = [
            {"role": "system", "content": "You are a restaurant review analyzer. Please provide structured responses separated by triple backticks as follows:"},
            {"role": "system", "content": "```Categories: Positive, Negative, Neutral``` ```Tags: Food Quality, Service, Ambiance, Price, Overall Experience``` ```Priority: High, Normal, Low``` ```Suggested Actions: Specify actions based on the feedback``` ```Generated Reply: Provide a first response to the customer based on the review sentiment```"},
            {"role": "user", "content": review}
        ]
    elif prompt_type == 2:  # Less specific prompt without few-shot examples
        messages = [
            {"role": "system", "content": "Analyze the review and provide categories, tags, priority, suggested actions, and a generated reply."},
            {"role": "user", "content": review}
        ]
    elif prompt_type == 3:  # Less directive prompt
        messages = [
            {"role": "system", "content": "Provide analysis of the review in terms of categories, tags, priority, actions, and reply."},
            {"role": "user", "content": review}
        ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300
    )
    response_text = response.choices[0].message.content.strip()
    log_message = f"Raw LLM Response for Prompt Type {prompt_type}: {response_text}"
    print(log_message)
    logging.info(log_message)  # Log the raw response

    # Check for triple backticks and parse accordingly
    if '```' in response_text:
        parts = response_text.split('```')
        data = {
            "Categories": parts[1].strip(),
            "Tags": parts[3].strip(),
            "Priority": parts[5].strip(),
            "Suggested Actions": parts[7].strip(),
            "Generated Reply": parts[9].strip()
        }
    else:
        data = {"Full Response": response_text}
    return data

output_paths = ['Detailed_Response.xlsx', 'Less_Specific_Response.xlsx', 'Less_Directive_Response.xlsx']

for i in range(1, 4):
    expanded_data = review_data['Review'].apply(lambda x: call_assistant(x, i)).apply(pd.Series)
    result_data = pd.concat([review_data, expanded_data], axis=1)
    # Save to different Excel files
    result_data.to_excel(output_paths[i-1], index=False)
    print(f"Responses for Prompt Type {i} have been saved to: {output_paths[i-1]}")
