import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


def generate_rgb_data(num_samples, height, width):
    return np.random.rand(num_samples, height, width, 3).astype("float32")


x_train = generate_rgb_data(10000, 28, 28)
x_test = generate_rgb_data(2000, 28, 28)

x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0


def add_noise(images):
    noise_factor = 0.5
    noisy_images = images + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=images.shape)
    noisy_images = np.clip(noisy_images, 0.0, 1.0)
    return noisy_images


x_train_noisy = add_noise(x_train)
x_test_noisy = add_noise(x_test)


def build_autoencoder(input_shape):
    model = models.Sequential()
    model.add(layers.InputLayer(input_shape=input_shape))
    model.add(layers.Conv2D(32, (3, 3), activation="relu", padding="same"))
    model.add(layers.MaxPooling2D((2, 2), padding="same"))
    model.add(layers.Conv2D(16, (3, 3), activation="relu", padding="same"))
    model.add(layers.MaxPooling2D((2, 2), padding="same"))
    model.add(layers.Conv2D(16, (3, 3), activation="relu", padding="same"))
    model.add(layers.UpSampling2D((2, 2)))
    model.add(layers.Conv2D(32, (3, 3), activation="relu", padding="same"))
    model.add(layers.UpSampling2D((2, 2)))
    model.add(layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same"))

    return model

input_shape = (28, 28, 3)
autoencoder = build_autoencoder(input_shape)

autoencoder.compile(optimizer="adam", loss="binary_crossentropy")

x_train_noisy = np.reshape(x_train_noisy, (len(x_train_noisy), 28, 28, 3))
x_test_noisy = np.reshape(x_test_noisy, (len(x_test_noisy), 28, 28, 3))
x_train = np.reshape(x_train, (len(x_train), 28, 28, 3))
x_test = np.reshape(x_test, (len(x_test), 28, 28, 3))

autoencoder.fit(x_train_noisy, x_train, epochs=50, batch_size=128, shuffle=True, validation_data=(x_test_noisy, x_test))

autoencoder.save("models/denoising_model.h5")
