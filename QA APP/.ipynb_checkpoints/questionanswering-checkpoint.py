# -*- coding: utf-8 -*-
"""QuestionAnswering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ItSobL6IFXPya4VR94o3KsaC7yW7RWzV
"""

from google.colab import drive
drive.mount('/content/drive')
root_path = '/content/drive/MyDrive/PROJECTS/Question Answering'

!pip install pdfplumber
!pip install -U gensim
!pip install transformers

import pdfplumber
import nltk
nltk.download('punkt')
import re
import gensim
import numpy
import pprint
import sklearn
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import torch

pdf_path='/content/drive/MyDrive/PROJECTS/Question Answering/Documents/DI.pdf'
with pdfplumber.open(pdf_path) as pdf:
    pdf_txt = ''
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        pdf_txt += page.extract_text()

tokens = nltk.sent_tokenize(pdf_txt)
for t in tokens:
    print(t, "\n")

from gensim.parsing.preprocessing import remove_stopwords
def clean_sentence(sentence, stopwords=False):
  sentence = sentence.lower().strip()
  sentence = re.sub(r'[^a-z0-9\s]', '', sentence)
  if stopwords:
    sentence = remove_stopwords(sentence)
  return sentence

def get_cleaned_sentences(tokens, stopwords=False):
  cleaned_sentences = []
  for row in tokens:
    cleaned = clean_sentence(row, stopwords)
    cleaned_sentences.append(cleaned)
  return cleaned_sentences

cleaned_sentences = get_cleaned_sentences(tokens, stopwords=True)
cleaned_sentences_with_stopwords = get_cleaned_sentences(tokens, stopwords=False)
print(cleaned_sentences)
print(cleaned_sentences_with_stopwords)

"""# cosine similiarity"""

sentences = cleaned_sentences_with_stopwords
sentence_words = [[word for word in document.split()]
                  for document in sentences]

from gensim import corpora
dictionary = corpora.Dictionary(sentence_words)
for key, value in dictionary.items():
  print(key, ' : ', value)

bow_corpus = [dictionary.doc2bow(text) for text in sentence_words]
for sent, embedding in zip(sentences, bow_corpus):
  print(sent)
  print(embedding)

user_question = "When was digital india launched ?"
question = clean_sentence(user_question, stopwords=False)
question_embedding = dictionary.doc2bow(question.split())
print(user_question, "\n", question_embedding)

from sklearn.metrics.pairwise import cosine_similarity

def retrieveAndPrintFAQAnswer(question_embedding, sentence_embeddings, sentences):
  max_sim = -1
  index_sim = -1
  for index, embedding in enumerate(sentence_embeddings):
    sim = cosine_similarity(embedding, question_embedding)[0][0]
    print(index, sim, sentences[index])
    if sim > max_sim:
      max_sim = sim
      index_sim = index

  return index_sim
index = retrieveAndPrintFAQAnswer(question_embedding, bow_corpus, sentences)

print("Question: ", question)
print("Answer: ", sentences[index])

"""# tf-idf vectorizer"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

stop_words = stopwords.words('english')

# Tokenize and preprocess the sentences
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(cleaned_sentences)

# Convert the user question into a TF-IDF vector
user_question ="When was digital india launched ?"
cleaned_user_question = ' '.join([word for word in nltk.word_tokenize(user_question) if word.isalnum() and word not in stop_words])
user_question_vector = vectorizer.transform([cleaned_user_question])

similarity_scores = cosine_similarity(user_question_vector, tfidf_matrix)

# Find the index of the most similar sentence
index_sim = similarity_scores.argmax()

print(user_question)
print(cleaned_sentences[index_sim])

"""#  Word2vec Model"""

from gensim.models import Word2Vec
import gensim.downloader as api

v2w_model = None
try:
  v2w_model = gensim.models.KeyedVectors.load('/content/drive/MyDrive/PROJECTS/Question Answering/w2vecmodel.mod')
  print("w2v Model Successfully loaded")
except:
  v2w_model = api.load('word2vec-google-news-300')
  v2w_model.save("/content/drive/MyDrive/PROJECTS/Question Answering/w2vecmodel.mod")
  print("w2v Model Saved")

w2vec_embedding_size = len(v2w_model['pc'])  # random word

def getWordVec(word, model):
  samp = model['pc']
  vec = [0]*len(samp)
  try:
    vec = model[word]
  except:
    vec = [0]*len(samp)
  return (vec) # embedding vector


def getPhraseEmbedding(phrase, embeddingmodel):
  samp = getWordVec('computer', embeddingmodel)
  vec = numpy.array([0]*len(samp))
  den = 0;
  for word in phrase.split():
    den = den+1
    vec = vec+numpy.array(getWordVec(word, embeddingmodel))
  return vec.reshape(1, -1) # phrase embedding vector

sent_embeddings = []
for sent in sentences:
  sent_embeddings.append(getPhraseEmbedding(sent, v2w_model))

question_embedding = getPhraseEmbedding(question, v2w_model)
index = retrieveAndPrintFAQAnswer(question_embedding, sent_embeddings, cleaned_sentences_with_stopwords)

print("Question: ", question)
print("Answer: ", cleaned_sentences_with_stopwords[index])

"""# Glove Embedding Approach"""

glove_model = None
try:
  glove_model = gensim.models.KeyedVectors.load('/content/drive/MyDrive/PROJECTS/Question Answering/glovemodel.mod')
  print("Glove Model Successfully loaded")
except:
  glove_model = api.load('glove-twitter-25')
  glove_model.save("/content/drive/MyDrive/PROJECTS/Question Answering/glovemodel.mod")
  print("Glove Model Saved")

glove_embedding_size = len(glove_model['pc'])

sent_embeddings = []
for sent in cleaned_sentences:
  sent_embeddings.append(getPhraseEmbedding(sent, glove_model))

question_embedding = getPhraseEmbedding(question, glove_model)
retrieveAndPrintFAQAnswer(question_embedding, sent_embeddings, cleaned_sentences_with_stopwords)

print("Question: ", question)
print("Answer: ", cleaned_sentences_with_stopwords[index])

"""# fasttext model"""

fasttext_model = None
try:
  fasttext_model = gensim.models.KeyedVectors.load('/content/drive/MyDrive/PROJECTS/Question Answering/fasttextmodel.mod')
  print("FastText Model Successfully loaded")
except:
  fasttext_model = api.load('fasttext-wiki-news-subwords-300')
  fasttext_model.save("/content/drive/MyDrive/PROJECTS/Question Answering/fasttextmodel.mod")
  print("FastText Model Saved")

fasttext_embedding_size = len(fasttext_model['example'])

sent_embeddings = []
for sent in cleaned_sentences:
  sent_embeddings.append(getPhraseEmbedding(sent, fasttext_model))

question_embedding = getPhraseEmbedding(question, fasttext_model)
retrieveAndPrintFAQAnswer(question_embedding, sent_embeddings, cleaned_sentences_with_stopwords)

print("Question: ", question)
print("Answer: ", cleaned_sentences_with_stopwords[index])

"""# BERT"""

from transformers import BertForQuestionAnswering, BertTokenizerFast
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizerFast.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

answer_text = pdf_txt
question = "What is digital India?"

# Apply the tokenizer to the input text, treating them as a text-pair.
encoded_inputs = tokenizer.encode_plus(question, answer_text, max_length=512, truncation=True, return_tensors='pt')
input_ids = encoded_inputs['input_ids']
token_type_ids = encoded_inputs['token_type_ids']
print('The input has a total of {:} tokens.'.format(len(input_ids[0])))

tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
for token, id in zip(tokens, input_ids[0]):
    if id == tokenizer.sep_token_id:
        print('')
    print('{:<12} {:>6,}'.format(token, id))

    if id == tokenizer.sep_token_id:
        print('')

# Calculate segment IDs
sep_index = input_ids[0].tolist().index(tokenizer.sep_token_id)
num_seg_a = sep_index + 1
num_seg_b = len(input_ids[0]) - num_seg_a
segment_ids = [0]*num_seg_a + [1]*num_seg_b
# Ensure segment IDs length matches input IDs length
assert len(segment_ids) == len(input_ids[0])

with torch.no_grad():
    outputs = model(input_ids, token_type_ids=token_type_ids)

start_scores_tensor = outputs.start_logits
end_scores_tensor = outputs.end_logits

start_scores = start_scores_tensor.squeeze().detach().tolist()
end_scores = end_scores_tensor.squeeze().detach().tolist()

# Find the start and end indices of the answer span in the token list
answer_start = torch.argmax(torch.tensor(start_scores))
answer_end = torch.argmax(torch.tensor(end_scores))

answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[0][answer_start:answer_end+1]))

print('Answer: "' + answer + '"')

answer = tokens[answer_start]
# Select the remaining answer tokens and join them with whitespace.
for i in range(answer_start + 1, answer_end + 1):
  # If it's a subword token, then recombine it with the previous token.
    if tokens[i][0:2] == '##':
        answer += tokens[i][2:]
        # Otherwise, add a space then the token.
    else:
        answer += ' ' + tokens[i]
print('Answer: "' + answer + '"')

# complete function
def answer_question(question, answer_text):
    # Tokenize inputs
    inputs = tokenizer.encode_plus(question, answer_text, max_length=512, truncation=True, return_tensors='pt')
    input_ids = inputs['input_ids']
    token_type_ids = inputs['token_type_ids']
    print('The input has a total of {:} tokens.'.format(len(input_ids[0])))

    # Calculate segment IDs
    sep_index = input_ids[0].tolist().index(tokenizer.sep_token_id)
    num_seg_a = sep_index + 1
    num_seg_b = len(input_ids[0]) - num_seg_a
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    # Ensure segment IDs length matches input IDs length
    assert len(segment_ids) == len(input_ids[0])
    # Generate answer scores using model
    with torch.no_grad():
        outputs = model(input_ids, token_type_ids=torch.tensor([segment_ids]))
        start_scores = outputs.start_logits.squeeze(dim=0)
        end_scores = outputs.end_logits.squeeze(dim=0)
    # Find answer start and end indices
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)
    # Convert answer token IDs to string
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[0][answer_start:answer_end+1]))
    # Calculate confidence score
    score = float(torch.max(torch.softmax(start_scores, dim=0)))
    # Return answer and score
    return answer, score

answer_question(question, answer_text)

"""Tokenization is the process of dividing a text string into smaller units known as tokens. In the context of BERT (Bidirectional Encoder Representations from Transformers), a popular language model, it is common to tokenize text into tokens with a maximum length of 512 tokens. This limitation arises from the maximum input length that BERT can handle effectively.

To perform tokenization for BERT, a common approach is to utilize the encode_plus method provided by tokenizers, a widely used library in conjunction with BERT. This method takes the original text as input and returns a list of tokens. It also incorporates special BERT tokens like [CLS], [SEP], and [PAD], which hold specific meanings within the BERT framework.

To control the token length, various parameters can be specified. For instance, the max_length parameter can be set to 512, indicating the desired length for the tokenized encodings. If the original text exceeds this limit, truncation can be enabled to remove any excess tokens beyond the specified maximum length.

Conversely, in cases where the original text is shorter than the desired length, padding can be applied. By setting padding to "max_length," the encoder pads the tokenized encodings with padding tokens until the desired length of 512 tokens is reached.

By utilizing these parameters within the encode_plus method, the text can be effectively tokenized into smaller units, special BERT tokens can be added, and the length of the resulting tokenized encodings can be controlled to adhere to BERT's maximum input length of 512 tokens.
"""

tokens = tokenizer.encode_plus(user_question, pdf_txt, add_special_tokens=True, max_length=512, truncation=True, padding="max_length")
tokens

"""It return a dictionary containing three key-value pairs, input_ids ,
token_type_ids , and attention_mask .
"""

# Added return_tensors='pt' to return PyTorch tensors from the tokenizer (rather than Python lists).
tokens = tokenizer.encode_plus(pdf_txt, add_special_tokens=False, return_tensors='pt')
tokens

input_id_chunks = tokens['input_ids'][0].split(510)
mask_chunks = tokens['attention_mask'][0].split(510)

for tensor in input_id_chunks:
  print(len(tensor))

"""***Chunk Preparation***

Now, we will divide our tokenized tensor into smaller chunks, each containing a maximum of 510 tokens. We chose this limit to leave room for the [CLS] and [SEP] tokens, as they require two additional positions.

***Splitting***

To accomplish this, we apply the split method to both our input IDs and attention mask tensors. Since we don't need the token type IDs, we can discard them. After splitting, we will have three chunks for each tensor set. It's important to note that we will need to add padding to the final chunk because it won't meet the required tensor size of 512, as specified by BERT.

***Adding [CLS] and [SEP] Tokens***

Next, we add the [CLS] (start of sequence) and [SEP] (separator) tokens. We can achieve this by using the torch.cat function, which concatenates a list of tensors. Since our tokens are already in token ID format, we can refer to the special tokens table mentioned earlier to create the token ID versions of [CLS] and [SEP]. Since we are performing this operation for multiple tensors, we will use a for-loop to concatenate the tokens individually for each chunk. Additionally, when concatenating the attention mask chunks, we use 1s instead of the values 101 and 102. This is because the attention mask doesn't contain token IDs but rather a series of 1s and 0s. In the attention mask, 0s represent the padding token locations, while [CLS] and [SEP] tokens, not being padding tokens, are represented by 1s.

***Padding***

To ensure that our tensor chunks meet the required length of 512 by BERT, we need to add padding. The first two chunks don't require any padding as they already meet this length requirement. However, the final chunks need padding. To determine if a chunk requires padding, we can use an if-statement to check the tensor length. If the tensor has fewer than 512 tokens, we can add padding using the torch.cat function. This statement should be added within the same for-loop where we added the [CLS] and [SEP] tokens.
"""

chunksize = 512

input_id_chunks = list(tokens['input_ids'][0].split(chunksize - 2))
mask_chunks = list(tokens['attention_mask'][0].split(chunksize - 2))

for i in range(len(input_id_chunks)):
    input_id_chunks[i] = torch.cat([
        torch.tensor([101]), input_id_chunks[i], torch.tensor([102])
    ])
    mask_chunks[i] = torch.cat([
        torch.tensor([1]), mask_chunks[i], torch.tensor([1])
    ])

    pad_len = chunksize - input_id_chunks[i].shape[0]
    if pad_len > 0:
        input_id_chunks[i] = torch.cat([
            input_id_chunks[i], torch.Tensor([0] * pad_len)
        ])
        mask_chunks[i] = torch.cat([
            mask_chunks[i], torch.Tensor([0] * pad_len)
        ])

for chunk in input_id_chunks:
    print(chunk)

# rejoining the splited tokens
for tensor in range(len(input_id_chunks)):
  ans = answer_question(user_question, ' '.join(tokenizer.convert_ids_to_tokens(input_id_chunks[tensor])))
  print(ans)

def expand_split_sentences(pdf_txt):
  new_chunks = nltk.sent_tokenize(pdf_txt)
  length = len(new_chunks)

  new_df = [];
  for i in range(length):
    paragraph = ""
    for j in range(i, length):
      tmp_token = tokenizer.encode(paragraph + new_chunks[j])
      length_token = len(tmp_token)
      if length_token < 510:
        paragraph = paragraph + new_chunks[j]
      else:
        break;
    new_df.append(paragraph)
  return new_df

fdi = pdf_txt

question_fdi = "When was digital india launched?"

max_score = 0;
final_answer = ""
new_df = expand_split_sentences(fdi)
for new_context in new_df:
  ans, score = answer_question(question_fdi, new_context)
  if score > max_score:
    max_score = score
    final_answer = ans
print(final_answer)
print(max_score)