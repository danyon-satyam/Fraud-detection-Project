#!/usr/bin/env python
# coding: utf-8

# 📘 Jupyter Notebook: Text Extraction and Analysis
# =====================================
# Author: Satyam Mohapatra
# -------------------------------------
# Date: 2024-12-21
# -------------------------------------
# Objective:
# To extract article text from URLs provided in Input.xlsx, clean the text using customized stopwords, and perform sentiment and readability analysis.

# 📂 Table of Contents:
#    1. Introduction
#    2. Setup and Imports
#    3. Data Extraction
#    4. Text Cleaning and Stopwords
#    5. Sentiment and Readability Analysis
#    6. Saving Results
#    7. Conclusion

# 1. 📖 Introduction <a id="introduction"></a>
# 
#     This notebook automates the process of web article extraction and analysis. Key tasks include:
#     - Extracting text from URLs.
#     - Cleaning and preprocessing the text by removing stopwords (currencies, dates, generic words, etc.).
#     - Performing sentiment analysis (positive/negative scores, polarity, subjectivity).
#     - Computing readability metrics (fog index, sentence length, word count).
#     - Exporting results to Output Data Structure.xlsx.

# 2. ⚙️ Setup and Imports <a id="setup-and-imports"></a>

# In[1]:


# Install necessary packages:
import os
os.system('pip install beautifulsoup4 selenium nltk openpyxl pandas syllapy requests --upgrade setuptools') 


# In[1]:


#Import required libraries:
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os
print(os.getcwd())
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk
import syllapy


# In[5]:


nltk.download('punkt')
nltk.download('stopwords')


# 3. 🌐 Data Extraction <a id="data-extraction"></a>
# 
#     Goal: Extract text content from URLs provided in Input.xlsx.

# In[9]:


#Code:
# Load URLs from Excel
import pandas as pd
import os

# Step 1: Ask the user for the path to the Excel file
input_path = input("Enter the path to Input.xlsx: ")

# Step 2: Read the Excel file (Handle errors if path is invalid)
try:
    df = pd.read_excel(input_path)
except FileNotFoundError:
    print("Error: File not found. Please check the path.")
    exit()

# Step 3: Prompt the user to specify where to save the CSV file
output_path = input("Enter the path to save the CSV file (e.g., C:/Users/Desktop/Input.csv): ")

# If user presses Enter without providing a path, save to current directory
if output_path.strip() == '':
    output_path = os.path.join(os.getcwd(), 'Input.csv')

# Step 4: Convert and save to CSV
df.to_csv(output_path, index=False)
print(f"Excel file converted and saved to: {output_path}")

# Directory to store extracted articles
os.makedirs('extracted_articles', exist_ok=True)

# Extract article text from URL
def extract_article(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_text = ' '.join([p.text for p in soup.find_all('p')])
        return article_text.strip()
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
        return ''
    
# Extract and save articles
for index, row in df.iterrows():
    article = extract_article(row['URL'])
    with open(f"extracted_articles/{row['URL_ID']}.txt", 'w', encoding='utf-8') as f:
        f.write(article)


# 4. ✂️ Text Cleaning and Stopwords <a id="text-cleaning-and-stopwords"></a>
# 
#     Goal: Remove irrelevant words (stopwords) from extracted text using custom stopword lists.
#     
#     Stopwords Include:
#     - Auditor names
#     - Currencies
#     - Dates and numbers
#     - Generic terms
#     - Geographic locations
#     - Common names

# In[10]:


#Code:
import os

def get_stopword_set(file_path):
    """
    Reads a file and returns its content as a set of words.
    Handles both UTF-8 and non-UTF-8 encoded files.
    """
    try:
        with open(file_path, 'rb') as file:
            byte_content = file.read()
            # Decode with error handling for non-UTF-8 files
            decoded_content = byte_content.decode('utf-8', errors='replace')
            return set(decoded_content.split())
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return set()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return set()

# Function to dynamically get file paths from the user
def get_file_paths():
    """
    Prompts the user to input file paths for various stopword files.
    """
    stopwords_files = {
        "Auditor": input("Enter path for StopWords_Auditor.txt: "),
        "Currencies": input("Enter path for StopWords_Currencies.txt: "),
        "Dates and Numbers": input("Enter path for StopWords_DatesandNumbers.txt: "),
        "Generic": input("Enter path for StopWords_Generic.txt: "),
        "GenericLong": input("Enter path for StopWords_GenericLong.txt: "),
        "Geographic": input("Enter path for StopWords_Geographic.txt: "),
        "Names": input("Enter path for StopWords_Names.txt: "),
    }
    return stopwords_files

# Get paths dynamically
file_paths = get_file_paths()

# Validate and process each file
stopwords_auditor = get_stopword_set(file_paths["Auditor"])
stopwords_currencies = get_stopword_set(file_paths["Currencies"])
stopwords_dates_numbers = get_stopword_set(file_paths["Dates and Numbers"])
stopwords_generic = get_stopword_set(file_paths["Generic"])
stopwords_genericlong = get_stopword_set(file_paths["GenericLong"])
stopwords_geographic = get_stopword_set(file_paths["Geographic"])
stopwords_names = get_stopword_set(file_paths["Names"])

# Combine all stopwords
custom_stopwords = (
    stopwords_auditor.union(
        stopwords_currencies,
        stopwords_dates_numbers,
        stopwords_generic,
        stopwords_genericlong,
        stopwords_geographic,
        stopwords_names
    )
)

# Output the size of the custom stopwords set as feedback
print(f"Custom stopwords set created with {len(custom_stopwords)} unique words.")


# 5. 📊 Sentiment and Readability Analysis <a id="sentiment-and-readability-analysis"></a>
# 
#    Goal: Perform sentiment and readability analysis to compute the following variables:
# 
#    - POSITIVE SCORE – Total count of positive words.
#    - NEGATIVE SCORE – Total count of negative words.
#    - POLARITY SCORE – Measures overall positivity or negativity of the text.
#    - SUBJECTIVITY SCORE – Indicates how subjective or objective the text is.
#    - AVG SENTENCE LENGTH – Average number of words per sentence.
#    - PERCENTAGE OF COMPLEX WORDS – Proportion of words with more than two syllables.
#    - FOG INDEX – Readability score indicating text complexity.
#    - AVG NUMBER OF WORDS PER SENTENCE – Average word count across sentences.
#    - COMPLEX WORD COUNT – Total count of words with more than two syllables.
#    - WORD COUNT – Total number of words (excluding stopwords).
#    - SYLLABLE PER WORD – Average syllable count per word.
#    - PERSONAL PRONOUNS – Count of personal pronouns like I, we, my, ours, us.
#    - AVG WORD LENGTH – Average character length of words.
# 

# In[21]:


#Code:
def load_word_set(file_path):
    """
    Reads a file and returns its content as a set of words.
    Handles both UTF-8 and non-UTF-8 encoded files.
    """
    try:
        with open(file_path, 'rb') as file:
            byte_content = file.read()
            decoded_content = byte_content.decode('utf-8', errors='replace')
            return set(decoded_content.split())
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return set()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return set()

def get_file_paths():
    """
    Prompts the user to input file paths for positive and negative word lists.
    """
    paths = {
        "Positive Words": input("Enter the path for positive-words.txt: "),
        "Negative Words": input("Enter the path for negative-words.txt: ")
    }
    return paths

# Get file paths dynamically
file_paths = get_file_paths()

# Load word sets
positive_words = load_word_set(file_paths["Positive Words"])
negative_words = load_word_set(file_paths["Negative Words"])

pos_dict = set(positive_words) 
neg_dict = set(negative_words)

def analyze_sentiment(text):
    words = word_tokenize(text.lower())
    sentences = sent_tokenize(text)
    words = [word for word in words if word.isalpha() and word not in custom_stopwords]
    
    # 1. Sentiment Analysis
    positive_score = sum(1 for word in words if word in pos_dict)
    negative_score = sum(1 for word in words if word in neg_dict)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)
    
    # 2. Readability and Complexity Analysis
    if len(sentences) > 0:
        avg_sentence_length = len(words) / len(sentences)
    else:
        avg_sentence_length = 0
    
    complex_words = [word for word in words if syllapy.count(word) > 2]
    percentage_complex = len(complex_words) / len(words) if len(words) > 0 else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex)
    
    # 3. Additional Metrics
    avg_number_of_words_per_sentence = len(words) / len(sentences) if len(sentences) > 0 else 0
    complex_word_count = len(complex_words)
    word_count = len(words)
    syllable_per_word = sum(syllapy.count(word) for word in words) / word_count if word_count > 0 else 0
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I))
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    # Return results as a dictionary
    return {
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': avg_sentence_length,
        'PERCENTAGE OF COMPLEX WORDS': percentage_complex,
        'FOG INDEX': fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': avg_number_of_words_per_sentence,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': word_count,
        'SYLLABLE PER WORD': syllable_per_word,
        'PERSONAL PRONOUNS': personal_pronouns,
        'AVG WORD LENGTH': avg_word_length
    }


# 6. 💾 Saving Results <a id="saving-results"></a>
# 
#     Goal: Save analysis results to an Excel file.

# In[25]:


#Code:
input_df = pd.read_excel(input_path)  # Load input data
results = []

for _, row in input_df.iterrows():
    url_id = row['URL_ID']
    file_path = f'extracted_articles/{url_id}.txt'
    
    # Process only if the file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
                if len(text.strip()) == 0:  # Skip empty files
                    print(f"Skipping empty file: {url_id}.txt")
                    continue

                # Perform Sentiment and Readability Analysis
                analysis = analyze_sentiment(text)
                result = {
                    'URL_ID': row['URL_ID'],      # From Input.xlsx
                    'URL': row['URL'],            # From Input.xlsx
                    **analysis                     # Add computed metrics
                }
                results.append(result)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

# Convert Results to DataFrame and Save
output_df = pd.DataFrame(results, columns=[
    'URL_ID', 'URL',                       # Columns from Input.xlsx
    'POSITIVE SCORE', 'NEGATIVE SCORE',    # Computed metrics
    'POLARITY SCORE', 'SUBJECTIVITY SCORE',
    'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS',
    'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE',
    'COMPLEX WORD COUNT', 'WORD COUNT',
    'SYLLABLE PER WORD', 'PERSONAL PRONOUNS',
    'AVG WORD LENGTH'
])

if not output_df.empty:
    output_df.to_excel('Output Data Structure.xlsx', index=False)
    print("Results saved to 'Output Data Structure.xlsx'")
else:
    print("No valid data to save.")


# 7. ✅ Conclusion <a id="conclusion"></a>
# 
#    This Python file automates the extraction and analysis of web articles, providing comprehensive insights through sentiment and readability metrics.  
