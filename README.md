This project is a smart restaurant management system that allows customers to browse the menu, place orders, and submit feedback, while the backend uses a trained RNN model to detect customer sentiment (positive, negative).
If negative sentiment is detected (e.g. “order was late”), the system automatically shows a sorry popup and generates a discount voucher to improve customer satisfaction.

How Sentiment Analysis Works?

 step 1.Customer submits feedback

 step 2.Text is cleaned and tokenized

 step.3 Converted to sequences using saved word_index.pkl

 step 4.Passed to LSTM model (sentiment_model.h5)

 step 5. Model predicts sentiment

 step 6.Django triggers:

  Apology popup + discount (Negative)

   Store normally (Positive/Neutral in postgresql database)







