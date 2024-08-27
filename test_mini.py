from utilities.llm_utils import *
import csv
import time
import random
import string

def test_gpt4o_mini_response_time():
    output_tokens = [20, 50, 100, 250, 500]
    input_tokens = [100, 1000, 10000, 16000]
    results = []

    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    for out_tokens in output_tokens:
        for in_tokens in input_tokens:
            input_text = " ".join([generate_random_string(random.randint(3, 10)) for _ in range(in_tokens // 4)])  # Approx. input tokens
            prompt_list = [
                {"role": "system", "content": f"You are a helpful assistant. Respond in exactly {out_tokens} tokens."},
                {"role": "user", "content": input_text}
            ]

            start_time = time.time()
            response = openai_response(prompt_list)
            end_time = time.time()

            response_time = end_time - start_time
            results.append([in_tokens, out_tokens, response_time])

    # Write results to CSV
    with open('tests4.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Input Tokens', 'Output Tokens', 'Response Time (s)'])
        writer.writerows(results)

# Run the test
if __name__ == "__main__":
    # test_gpt4o_mini_response_time()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Read the CSV file
    df = pd.read_csv('tests4.csv')
    
    # Pivot the data to create a 2D matrix
    pivot_df = df.pivot(index='Input Tokens', columns='Output Tokens', values='Response Time (s)')
    
    # Create a figure and axis
    plt.figure(figsize=(12, 8))
    
    # Create a heatmap
    sns.heatmap(pivot_df, annot=True, fmt='.2f', cmap='Greens', cbar_kws={'label': 'Response Time (s)'})
    
    # Set labels and title
    plt.xlabel('Output Tokens')
    plt.ylabel('Input Tokens')
    plt.title('GPT-3.5-turbo Response Times')
    
    # Adjust layout and save the plot
    plt.tight_layout()
    plt.savefig('gpt3.5_turbo_response_times.png')
    plt.close()