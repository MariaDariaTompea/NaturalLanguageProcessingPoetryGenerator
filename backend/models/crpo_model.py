import tensorflow as tf
from tensorflow.keras.layers import LSTM, Embedding, Dense, Bidirectional, Attention, Input, Concatenate
from tensorflow.keras.models import Model

class CRPOModel:
    def __init__(self, vocab_size, seq_length=40):
        self.vocab_size = vocab_size
        self.seq_length = seq_length
        self.model = self._build_model()

    def _build_model(self):
        # Makale: 40 birimlik giriş, 100 birimlik embedding [cite: 142]
        inputs = Input(shape=(self.seq_length,))
        x = Embedding(self.vocab_size, 100)(inputs) 
        
        # Makale: 256 birimlik iki yönlü LSTM (her yön 128) [cite: 142]
        lstm_1 = Bidirectional(LSTM(128, return_sequences=True))(x)
        lstm_2 = Bidirectional(LSTM(128, return_sequences=True))(lstm_1)
        
        # Makale: Embedding ve LSTM katmanlarının birleşimi üzerinde Attention [cite: 143]
        lstm_reduced = Dense(100)(lstm_2) 
        query_value_attention = Attention()([x, lstm_reduced])
        
        merged = Concatenate()([query_value_attention, lstm_2])
        # Makale: 89 birimlik Softmax çıktı katmanı (karakter seti boyutu) [cite: 143]
        outputs = Dense(self.vocab_size, activation='softmax')(merged[:, -1, :])
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        return model