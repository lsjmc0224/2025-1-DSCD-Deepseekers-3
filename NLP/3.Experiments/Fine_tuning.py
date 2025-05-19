import os
import random
import numpy as np
import pandas as pd
import tensorflow as tf
from transformers import (
    BertTokenizer,
    TFBertForSequenceClassification,
    TFElectraForSequenceClassification,
    TFAlbertForSequenceClassification,
    TFRobertaForSequenceClassification
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# set random seeds (optional)
# def set_seed(seed=42):
#     random.seed(seed)
#     np.random.seed(seed)
#     tf.random.set_seed(seed)
# set_seed(42)

# ----------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------
def to_categorical(y, num_classes=None):
    y = np.array(y, dtype='int')
    if num_classes is None:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=np.float32)
    categorical[np.arange(n), y] = 1
    return categorical

# ----------------------------------------------------------------------------
# Custom Models with train/test steps
# ----------------------------------------------------------------------------
class CustomMixin:
    @staticmethod
    def custom_unpack(data):
        if isinstance(data, tuple):
            if len(data) == 2:
                return data[0], data[1], None
            elif len(data) == 3:
                return data
        return data, None, None

    def train_step(self, data):
        x, y, sw = self.custom_unpack(data)
        with tf.GradientTape() as tape:
            logits = self(x, training=True)
            loss = self.compiled_loss(y, logits, sw, regularization_losses=self.losses)
        grads = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.trainable_variables))
        self.compiled_metrics.update_state(y, logits, sw)
        return {m.name: m.result() for m in self.metrics}

    def test_step(self, data):
        x, y, sw = self.custom_unpack(data)
        logits = self(x, training=False)
        loss = self.compiled_loss(y, logits, sw, regularization_losses=self.losses)
        self.compiled_metrics.update_state(y, logits, sw)
        return {m.name: m.result() for m in self.metrics}

class CustomTFBertForSequenceClassification(CustomMixin, TFBertForSequenceClassification):
    pass

class CustomTFElectraForSequenceClassification(CustomMixin, TFElectraForSequenceClassification):
    pass

class CustomTFAlbertForSequenceClassification(CustomMixin, TFAlbertForSequenceClassification):
    pass

class CustomTFRobertaForSequenceClassification(CustomMixin, TFRobertaForSequenceClassification):
    pass

# ----------------------------------------------------------------------------
# Training & Evaluation Function
# ----------------------------------------------------------------------------
def train_and_evaluate(
    model_name: str,
    model_class,
    tokenizer_name: str,
    batch_size: int,
    learning_rate: float,
    max_length: int,
    X_train, y_train, X_test, y_test
):
    tokenizer = BertTokenizer.from_pretrained(tokenizer_name)
    model = model_class.from_pretrained(model_name, num_labels=2, from_pt=True)

    # Tokenize datasets
    train_tok = tokenizer(
        X_train, return_tensors="tf",
        max_length=max_length, padding='max_length', truncation=True
    )
    test_tok  = tokenizer(
        X_test, return_tensors="tf",
        max_length=max_length, padding='max_length', truncation=True
    )

    train_ds = tf.data.Dataset.from_tensor_slices((dict(train_tok), y_train)) \
                      .shuffle(len(X_train)).batch(batch_size)
    test_ds  = tf.data.Dataset.from_tensor_slices((dict(test_tok), y_test)) \
                      .batch(batch_size)

    optimizer = tf.keras.optimizers.Adam(learning_rate)
    loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    # Callbacks
    es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, verbose=1, mode='min') #얼리스탑 5 급하면 3 
    ckpt_path = os.path.join(
        os.getcwd(),
        f"checkpoint_{model_name.replace('/', '_')}_maxlen_{max_length}"
    )
    mc = tf.keras.callbacks.ModelCheckpoint(
        ckpt_path, save_best_only=True, save_weights_only=True,
        monitor='val_loss', mode='min'
    )

    history = model.fit(
        train_ds,
        epochs=500,
        validation_data=test_ds,
        callbacks=[es, mc]
    )

    # Load best weights and evaluate
    model.load_weights(ckpt_path)
    preds = model.predict(test_ds)
    probs = tf.nn.softmax(preds.logits, axis=1).numpy()
    y_pred = np.argmax(probs, axis=1)
    y_true = np.argmax(y_test, axis=1)

    report = classification_report(y_true, y_pred, output_dict=True)
    metrics = {
        'accuracy': report['accuracy'],
        'precision': report['weighted avg']['precision'],
        'recall': report['weighted avg']['recall'],
        'f1': report['weighted avg']['f1-score'],
        'epochs_trained': len(history.history['loss'])
    }
    return metrics

# ----------------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    # ── 1) 데이터 로드 ──
    data_dir  = r"C:\Users\parkm\OneDrive - dgu.ac.kr\DC\JICS-NLP-2024\1.Data"
    train_csv = os.path.join(data_dir, 'train_data_v3.csv')
    test_csv  = os.path.join(data_dir, 'test_data_1000.csv')

    # 학습 데이터
    df_train = pd.read_csv(train_csv, encoding='utf-8')
    X_train  = df_train['comment'].tolist()
    y_train  = df_train['sentiment'].astype(int).values
    y_train  = to_categorical(y_train)

    # 테스트 데이터
    df_test  = pd.read_csv(test_csv, encoding='utf-8')
    X_test   = df_test['comment'].tolist()
    y_test   = df_test['sentiment'].astype(int).values
    y_test   = to_categorical(y_test)

    # ── 2) 공통 설정 ──
    common_cfg = {
        'model_name':     'beomi/KcELECTRA-base-v2022',
        'model_class':    CustomTFElectraForSequenceClassification,
        'tokenizer_name': 'beomi/KcELECTRA-base-v2022',
        'batch_size':     16, #32
        'learning_rate':  2e-5
    }

    # ── 3) max_length 64,128 두 가지만 돌리기 ──
    results = []
    for max_length in [64, 128]:
        metrics = train_and_evaluate(
            **common_cfg,
            max_length = max_length,
            X_train    = X_train,
            y_train    = y_train,
            X_test     = X_test,
            y_test     = y_test
        )
        metrics['max_length'] = max_length
        results.append(metrics)

    # ── 4) 결과 저장/출력 ──
    df = pd.DataFrame(results)
    df.to_csv("model_comparison_64_128.csv", index=False)
    print(df)


# if __name__ == '__main__':
#     # Example usage
#     data_dir = r"C:\Users\parkm\OneDrive - dgu.ac.kr\DC\JICS-NLP-2024\1.Data"
#     train_csv = os.path.join(data_dir, 'train_data_v3.csv')
#     test_csv  = os.path.join(data_dir, 'test_data_1000.csv')

#     df_train = pd.read_csv(train_csv)
#     X = df_train['comment'].tolist()
#     y = df_train['sentiment'].astype(int).values
#     y = to_categorical(y)
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

#     cfg = {
#         'model_name': 'beomi/KcELECTRA-base-v2022',
#         'model_class': CustomTFElectraForSequenceClassification,
#         'tokenizer_name': 'beomi/KcELECTRA-base-v2022',
#         'batch_size': 16,
#         'learning_rate': 2e-5,
#         'max_length': 64
#     }
#     results = train_and_evaluate(**cfg, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)
#     print(results)


# import tensorflow as tf
# import numpy as np
# import pandas as pd
# from transformers import BertTokenizer, TFElectraForSequenceClassification, TFBertForSequenceClassification, TFAlbertForSequenceClassification, TFRobertaForSequenceClassification
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report
# import random
# from transformers import TFElectraForSequenceClassification, BertTokenizer
# import os
# # def set_seed(seed=42): 
# #     random.seed(seed) 
# #     np.random.seed(seed)
# #     tf.random.set_seed(seed)
    
# # set_seed(42)



# print(tf.config.list_physical_devices('GPU'))
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# gpus = tf.config.experimental.list_physical_devices('GPU')

# if gpus:
#     # 이 블록엔 이제 들어오지 않습니다
#     try:
#         for gpu in gpus:
#             tf.config.experimental.set_memory_growth(gpu, True)
#         print(f"GPUs {gpus} are available and set for memory growth.")
#     except RuntimeError as e:
#         print(e)
# else:
#     print("No GPUs are available.  → Running on CPU only")
# # gpus = tf.config.experimental.list_physical_devices('GPU')
# # if gpus:
# #     try:
# #         for gpu in gpus:
# #             tf.config.experimental.set_memory_growth(gpu, True)
# #         print(f"GPUs {gpus} are available and set for memory growth.")
# #     except RuntimeError as e:
# #         print(e)
# # else:
# #     print("No GPUs are available.")

# def to_categorical(y, num_classes=None):
#     y = np.array(y, dtype='int')
#     input_shape = y.shapeS
#     if num_classes is None:
#         num_classes = np.max(y) + 1
#     n = y.shape[0]
#     categorical = np.zeros((n, num_classes))
#     categorical[np.arange(n), y] = 1
#     return categorical

# def load_data(file_path):
#     with open(file_path, encoding='utf-8') as f:
#         docs = [doc.strip().split('\t') for doc in f]
#         docs = [(doc[0], int(doc[1])) for doc in docs if len(doc) == 2]
#         texts, labels = zip(*docs)
#         y_one_hot = to_categorical(labels)
#         return train_test_split(texts, y_one_hot, test_size=0.2, random_state=0)
    
# class CustomTFBertForSequenceClassification(TFBertForSequenceClassification):
#     @staticmethod
#     def custom_unpack_x_y_sample_weight(data):
#         if isinstance(data, tuple):
#             if len(data) == 2:
#                 return data[0], data[1], None
#             elif len(data) == 3:
#                 return data
#         return data, None, None

#     def train_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         with tf.GradientTape() as tape:
#             y_pred = self(x, training=True)
#             loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         gradients = tape.gradient(loss, self.trainable_variables)
#         self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

#     def test_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         y_pred = self(x, training=False)
#         loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

# class CustomTFElectraForSequenceClassification(TFElectraForSequenceClassification):
#     @staticmethod
#     def custom_unpack_x_y_sample_weight(data):
#         if isinstance(data, tuple):
#             if len(data) == 2:
#                 return data[0], data[1], None
#             elif len(data) == 3:
#                 return data
#         return data, None, None

#     def train_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         with tf.GradientTape() as tape:
#             y_pred = self(x, training=True)
#             loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         gradients = tape.gradient(loss, self.trainable_variables)
#         self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

#     def test_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         y_pred = self(x, training=False)
#         loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

# class CustomTFAlbertForSequenceClassification(TFAlbertForSequenceClassification):
#     @staticmethod
#     def custom_unpack_x_y_sample_weight(data):
#         if isinstance(data, tuple):
#             if len(data) == 2:
#                 return data[0], data[1], None
#             elif len(data) == 3:
#                 return data
#         return data, None, None

#     def train_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         with tf.GradientTape() as tape:
#             y_pred = self(x, training=True)
#             loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         gradients = tape.gradient(loss, self.trainable_variables)
#         self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

#     def test_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         y_pred = self(x, training=False)
#         loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

# class CustomTFRobertaForSequenceClassification(TFRobertaForSequenceClassification):
#     @staticmethod
#     def custom_unpack_x_y_sample_weight(data):
#         if isinstance(data, tuple):
#             if len(data) == 2:
#                 return data[0], data[1], None
#             elif len(data) == 3:
#                 return data
#         return data, None, None

#     def train_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         with tf.GradientTape() as tape:
#             y_pred = self(x, training=True)
#             loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         gradients = tape.gradient(loss, self.trainable_variables)
#         self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

#     def test_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         y_pred = self(x, training=False)
#         loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

# class CustomTFKcBertForSequenceClassification(TFBertForSequenceClassification):
#     @staticmethod
#     def custom_unpack_x_y_sample_weight(data):
#         if isinstance(data, tuple):
#             if len(data) == 2:
#                 return data[0], data[1], None
#             elif len(data) == 3:
#                 return data
#         return data, None, None

#     def train_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         with tf.GradientTape() as tape:
#             y_pred = self(x, training=True)
#             loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         gradients = tape.gradient(loss, self.trainable_variables)
#         self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}

#     def test_step(self, data):
#         x, y, sample_weight = self.custom_unpack_x_y_sample_weight(data)
#         y_pred = self(x, training=False)
#         loss = self.compiled_loss(y, y_pred, sample_weight, regularization_losses=self.losses)
#         self.compiled_metrics.update_state(y, y_pred, sample_weight)
#         return {m.name: m.result() for m in self.metrics}
# #만진부분
# import os
# # ─────────────── 데이터 파일 경로 ───────────────
# data_dir   = r"C:\Users\parkm\OneDrive - dgu.ac.kr\DC\JICS-NLP-2024\1.Data"
# train_csv  = os.path.join(data_dir, "train_data_v3.csv")
# test_csv   = os.path.join(data_dir, "test_data_1000.csv")

# # ─────────────── 1) train 데이터 불러오기 ───────────────
# train_df = pd.read_csv(train_csv, encoding='utf-8')
# # 'comment'와 'sentiment' 열만 남기기
# train_df = train_df[['comment', 'sentiment']]
# X_train  = train_df['comment'].tolist()
# y_train  = train_df['sentiment'].astype(int).values

# # ─────────────── 2) test 데이터 불러오기 ───────────────
# test_df = pd.read_csv(test_csv, encoding='utf-8')
# # 역시 'comment'와 'sentiment'만 사용
# test_df = test_df[['comment', 'sentiment']]
# X_test  = test_df['comment'].tolist()
# y_test  = test_df['sentiment'].astype(int).values

# # ─────────────── 3) 원-핫 인코딩 (기존 to_categorical 함수 사용) ───────────────
# y_train = to_categorical(y_train)
# y_test  = to_categorical(y_test)
# #여까지

# # 원래: def train_and_evaluate(model_name, model_class, tokenizer_name, batch_size, learning_rate, max_length):
# # 바꿔서: X_train, y_train, X_test, y_test를 인자로 받도록 합니다.
# def train_and_evaluate(model_name,
#                        model_class,
#                        tokenizer_name,
#                        batch_size,
#                        learning_rate,
#                        max_length,
#                        X_train, y_train,
#                        X_test,  y_test):
#     tokenizer = BertTokenizer.from_pretrained(tokenizer_name)
#     # … 이후 내부에서는 load_data 대신 넘겨받은 X_train, y_train, X_test, y_test 사용

#     model = model_class.from_pretrained(model_name, num_labels=2, from_pt=True)
    
#     X_train_tokenized = tokenizer(X_train, return_tensors="tf", max_length=max_length, padding='max_length', truncation=True)
#     X_test_tokenized = tokenizer(X_test, return_tensors="tf", max_length=max_length, padding='max_length', truncation=True)
    
#     train_dataset = tf.data.Dataset.from_tensor_slices((dict(X_train_tokenized), y_train)).shuffle(len(y_train)).batch(batch_size)
#     test_dataset = tf.data.Dataset.from_tensor_slices((dict(X_test_tokenized), y_test)).batch(batch_size)

#     optimizer = tf.keras.optimizers.Adam(learning_rate)
#     loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
#     model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    
#     es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=10)
#     checkpoint_filepath = rf"C:\Users\parkm\OneDrive - dgu.ac.kr\DC\JICS-NLP-2024\checkpoints_{model_name.replace('/', '_')}_maxlen_{max_length}"

#     mc = tf.keras.callbacks.ModelCheckpoint(checkpoint_filepath, monitor='val_loss', mode='min', 
#                                             save_best_only=True, save_weights_only=True)
    

#     memory_usage = []

#     # class MemoryCallback(tf.keras.callbacks.Callback):
#     #     def on_epoch_end(self, epoch, logs=None):
#     #         memory_info = tf.config.experimental.get_memory_info('GPU:0')
#     #         memory_usage.append(memory_info['current'])
#     # 1) 콜백 정의부
#     class MemoryCallback(tf.keras.callbacks.Callback):
#         def on_epoch_end(self, epoch, logs=None):
#             # GPU가 하나라도 있으면 메모리 정보 수집
#             if tf.config.list_physical_devices('GPU'):
#                 info = tf.config.experimental.get_memory_info('GPU:0')
#                 memory_usage.append(info['current'])

#     memory_callback = MemoryCallback()

#     # 2) 콜백 등록부
#     callbacks = [es, mc]  # EarlyStopping, ModelCheckpoint
#     if tf.config.list_physical_devices('GPU'):
#         callbacks.append(memory_callback)

#     # 3) 학습
#     history = model.fit(
#         train_dataset,
#         epochs=800,
#         validation_data=test_dataset,
#         callbacks=callbacks
#     )

        
    
#     #history = model.fit(train_dataset, epochs=800, validation_data=test_dataset, callbacks=[es, mc, memory_callback])
    

#     average_memory_usage = np.mean(memory_usage)
    
#     model.load_weights(checkpoint_filepath)
#     y_preds = model.predict(test_dataset)
#     prediction_probs = tf.nn.softmax(y_preds.logits, axis=1).numpy()
#     y_predictions = np.argmax(prediction_probs, axis=1)
#     y_test_labels = np.argmax(y_test, axis=1)
    
#     report = classification_report(y_test_labels, y_predictions, output_dict=True)
#     accuracy = report['accuracy']
#     recall = report['weighted avg']['recall']
#     precision = report['weighted avg']['precision']
#     f1 = report['weighted avg']['f1-score']
    
#     epochs_trained = len(history.history['loss'])
    

#     tf.keras.backend.clear_session()
    
#     #tf.config.experimental.reset_memory_stats('GPU:0')
    
#     return accuracy, recall, precision, f1, epochs_trained, average_memory_usage

# results = []

# model_configs = [
#     # {"model_name": "kykim/albert-kor-base", "model_class": CustomTFAlbertForSequenceClassification, "tokenizer_name": "kykim/albert-kor-base"},
#     # {"model_name": "klue/bert-base", "model_class": CustomTFBertForSequenceClassification, "tokenizer_name": "klue/bert-base"},
#     # {"model_name": "klue/roberta-base", "model_class": CustomTFRobertaForSequenceClassification, "tokenizer_name": "klue/roberta-base"},
#     # {"model_name": "beomi/kcbert-base", "model_class": CustomTFKcBertForSequenceClassification, "tokenizer_name": "beomi/kcbert-base"},
#     {"model_name": "beomi/KcELECTRA-base-v2022", "model_class": CustomTFElectraForSequenceClassification, "tokenizer_name": "beomi/KcELECTRA-base-v2022"}
# ]

# batch_size = 16
# learning_rate = 2e-5
# max_lengths = [16, 32, 64, 128]


# results = []
# for config in model_configs:
#     for max_length in max_lengths:
#         accuracy, recall, precision, f1, epochs, avg_mem = train_and_evaluate(
#             config["model_name"],
#             config["model_class"],
#             config["tokenizer_name"],
#             batch_size,
#             learning_rate,
#             max_length,
#             X_train, y_train,
#             X_test,  y_test
#         )
#         results.append((config["model_name"],
#                         max_length,
#                         accuracy, recall,
#                         precision, f1,
#                         epochs, avg_mem))


# results_df = pd.DataFrame(results, columns=["Model Name", "Max Length", "Accuracy", "Recall", "Precision", "F1-Score", "Epochs Trained", "Average Memory Usage (MB)"])
# results_df.to_csv('model_comparison_memory_usage3_0510.csv', index=False)
# print(results_df)
# # … 모든 함수·클래스 정의 끝나고

# if __name__ == "__main__":
    
#     # 학습 루프만 여기에 남기고
#     results = []
#     for config in model_configs:
#         for max_length in max_lengths:
#             accuracy, recall, precision, f1, epochs_trained, avg_mem = train_and_evaluate(
#                 config["model_name"],
#                 config["model_class"],
#                 config["tokenizer_name"],
#                 batch_size,
#                 learning_rate,
#                 max_length,
#                 X_train, y_train,
#                 X_test, y_test
#             )
#             results.append((
#                 config["model_name"],
#                 max_length,
#                 accuracy, recall,
#                 precision, f1,
#                 epochs_trained, avg_mem
#             ))

#     import pandas as pd
#     df = pd.DataFrame(
#         results,
#         columns=[
#             "model_name","max_length","accuracy","recall",
#             "precision","f1_score","epochs_trained","avg_mem_usage"
#         ]
#     )
#     df.to_csv("model_comparison.csv", index=False)
#     print(df)