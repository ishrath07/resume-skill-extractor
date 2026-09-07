import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple hired a React developer in Seattle in 2021.")

for token in doc:
    print(token.text, token.pos_)

for ent in doc.ents:
    print(ent.label_, ent.text)