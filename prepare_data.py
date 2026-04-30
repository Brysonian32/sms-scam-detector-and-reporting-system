import pandas as pd

print("Script started...")

# Load UK dataset with correct encoding
uk_data = pd.read_csv('dataset/spam.csv', encoding='latin-1')

# Load Swahili dataset
swahili_data = pd.read_csv('dataset/swahili_dataset.csv')

# Rename trust -> ham
swahili_data['label'] = swahili_data['label'].replace({'trust': 'ham'})

# Combine datasets
combined_data = pd.concat([uk_data, swahili_data], ignore_index=True)

# Save combined dataset
combined_data.to_csv('dataset/combined_sms_spam.csv', index=False)

print("Dataset combined successfully!")
