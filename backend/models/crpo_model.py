"""
Deep Learning model for character-based poetry generation.
Uses Bidirectional LSTMs and Attention mechanism to learn poetic structures.
"""
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Embedding, Dense, Bidirectional, Attention, Input, Concatenate
from tensorflow.keras.models import Model

class CRPOModel:
    def __init__(self, vocab_size, seq_length=40):
        # Defines the vocabulary size and input sequence length
        self.vocab_size = vocab_size
        self.seq_length = seq_length
        self.model = self._build_model()

    def _build_model(self):
        # Creates the neural network architecture with LSTM and Attention layers
        inputs = Input(shape=(self.seq_length,))
        x = Embedding(self.vocab_size, 100)(inputs) 
        
        lstm_1 = Bidirectional(LSTM(128, return_sequences=True))(x)
        lstm_2 = Bidirectional(LSTM(128, return_sequences=True))(lstm_1)
        
        lstm_reduced = Dense(100)(lstm_2) 
        query_value_attention = Attention()([x, lstm_reduced])
        
        merged = Concatenate()([query_value_attention, lstm_2])
        outputs = Dense(self.vocab_size, activation='softmax')(merged[:, -1, :])
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        return model