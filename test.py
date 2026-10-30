from paperrag.embed import embed_texts

a, b, c = embed_texts(['a cat sat on the mat', 'a kitten rests on a rug', 'quarterly tax filing deadlines'])
print(a @ b, a @ c) 