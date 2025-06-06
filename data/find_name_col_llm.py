from transformers import pipeline

# Load the NER pipeline using the model
ner = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

text = "Starbucks"

entities = ner(text)
print(entities)

