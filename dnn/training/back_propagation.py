
# coding: utf-8

# In[ ]:


# Authors: Daichi Yoshikawa <daichi.yoshikawa@gmail.com>
# License: BSD 3 clause

from __future__ import absolute_import

import sys
import copy
import numpy as np
from collections import OrderedDict

from .loss_function import LossFunctionFactory
from .loss_function import MultinomialCrossEntropy
from .loss_function import BinomialCrossEntropy
from .loss_function import SquaredError
from .learning_curve import LearningCurve
from ..utils.nn_utils import shuffle_data


class BackPropagation:
    """Back propagation algorithm to update weights of neural network.

    Parameters
    ----------
    epochs : int
        Number of all data scanning.
    batch_size : int
        Mini batch size. This number of data are treated
        at the same time for one update of weight.
    optimizer : Derived class of Optimizer
            Instance of derived class of Optimizer.
    optimizers : OrderedDict of derived class of Optimizer
        Optimizers to update weights based on error.
        These are created only for layer,
        which has weight parameter, like affine layer.
    loss_function : Derived class of LossFunction
        Used to calculate loss.
    lc : LearningCurve
        Used to display evaluation results and
        plot learning curve. Returned by fit method.
    dtype : type
        Data type of variables. Generally float64 or float32.
    """
    def __init__(
            self,
            epochs,
            batch_size,
            optimizer,
            loss_function,
            learning_curve,
            dtype):
        """
        Arguments
        ---------
        epochs : int
            Number of all data scanning.
        batch_size : int
            Mini batch size. This number of data are treated
            at the same time for one update of weight .
        optimizer : Derived class of Optimizer
            Instance of derived class of Optimizer.
        loss_function : LossFunction.Type
            Type of loss function.
            Generally, cross entropy is used for classification and
            squared error is used for regression.
        learning_curve : bool
            Prints out evaluation results of ongoing training.
            Also, returns learning curve after completion of training.
        dtype : type
            Data type of variables. Generally float64 or float32.
        """
        self.epochs = epochs
        self.batch_size = batch_size
        self.optimizer = optimizer
        self.optimizers = OrderedDict()
        self.loss_function = LossFunctionFactory.get(
                loss_function=loss_function)
        self.lc = LearningCurve(dtype=dtype) if learning_curve else None
        self.dtype = dtype

    def fit(self, layers, x_train, y_train, x_test, y_test, shuffle_per_epoch):
        """Train prediction model based on training data.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configure neural network.
        x_train : np.array
            Descriptive features in 2d array, which is used to train model.
            x_train.shape == (num of data, num of feature)
        y_train : np.array
            Target features in 2d array, which is used to train model.
            y_train.shape == (num of data, num of feature)
        x_test : np.array
            Descriptive features in 2d array, which is used to evaluate model.
            x_test.shape == x_train.shape
        y_test : np.array
            Target features in 2d array, which is used to evaluate model.
            y_test.shape == y_train.shape
        shuffle_per_epoch : bool
            If true, shuffle training data per each epoch.
        """
        self.__initialize_optimizers(layers)

        for epoch in range(self.epochs):
            if shuffle_per_epoch:
                x_train, y_train = shuffle_data(x_train, y_train)

            self.__train_one_epoch(layers, x_train, y_train)
            self.__evaluate(layers, x_train, y_train, x_test, y_test, epoch)

        self.__finalize_training(layers, x_train)

        return self.lc

    def __finalize_training(self, layers, x):
        """This method is called after completion of training.

        Optimizer or layer might require some finilization after training.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configure neural network.
        x : np.array
            Descriptive features in 2d array.
            x_train.shape == (num of data, num of feature)
        """
        layers[0].finalize_training(x)

    def __train_one_epoch(self, layers, x_train, y_train):
        """Implements training for one epoch.

        In one epoch, data is splitted into multiple bathes based on
        batch size. Weights are updated per a batch.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configures of neural network.
        x_train : np.array
            Descriptive features in 2d array, which is used to train model.
            x_train.shape == (num of data, num of feature)
        y_train : np.array
            Target features in 2d array, which is used to train model.
            y_train.shape == (num of data, num of feature)
        """
        data_num = x_train.shape[0]

        for i in range(0, data_num, self.batch_size):
            end = i + self.batch_size

            if end > data_num:
                end = data_num

            self.__train_one_batch(layers, x_train[i:end], y_train[i:end])
            sys.stdout.write('\r%2.2f%% ' % (100. * i / data_num))
        sys.stdout.write('\r100.00% ')

    def __train_one_batch(self, layers, x_train, y_train):
        """Implements one update of weights of neural network.

        In order to update weights, forward calculation is needed firstly.
        With the resulting forward output, backward calculation is done.
        And then, update weights based on propagated errors in each layers.
        The update behaves differently depending on optimizer you use.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configure neural network.
        x_train : np.array
            Descriptive features in 2d array, which is used to train model.
            x_train.shape == (num of data, num of feature)
        y_train : np.array
            Target features in 2d array, which is used to train model.
            y_train.shape == (num of data, num of feature)
        """
        layers[0].forward(x_train)
        layers[-1].backward(layers[-1].fire - y_train)
        self.__optimize_network(layers)

    def __initialize_optimizers(self, layers):
        """Create instances of optimizer for each layer which has weights in it.

        Optimizer is required to update weights of neural network.
        Since optimizer sometimes has to store some parameters for each layer,
        each layer is supposed to be each optimizer's instance.
        Also, layer which doesn't have weights shouldn't have optimizer.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configure neural network.
        """
        self.optimizers = OrderedDict()

        for i, layer in enumerate(layers, 1):
            if layer.has_weight() is True:
                self.optimizers[i] = copy.deepcopy(self.optimizer)

    def __optimize_network(self, layers):
        """Update weights by optimizers.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configure neural network.
        """
        for i, layer in enumerate(layers, 1):
            if layer.has_weight() is True:
                self.optimizers[i].optimize(layer.w, layer.dw)

    def __evaluate(self, layers, x_train, y_train, x_test, y_test, epoch):
        """Evaluate loss of model under training.

        If test data is empty, doesn't display loss w.r.t test data.
        If you select squared error as loss function,
        accuracy will not displayed.

        Arguments
        ---------
        layers : list or np.array of Layer
            All layers which configures of neural network.
        x_train : np.array
            Descriptive features in 2d array, which is used to train model.
            x_train.shape == (num of data, num of feature)
        y_train : np.array
            Target features in 2d array, which is used to train model.
            y_train.shape == (num of data, num of feature)
        x_test : np.array
            Descriptive features in 2d array, which is used to evaluate model.
            x_test.shape == x_train.shape
        y_test : np.array
            Target features in 2d array, which is used to evaluate model.
            y_test.shape == y_train.shape
        epoch : int
            Number of epoch.
        """
        y_test_pred = None
        loss_test = None
        acc_train = None
        acc_test = None

        y_train_pred = layers[0].predict(x_train)
        loss_train = self.loss_function.get(y=y_train_pred, t=y_train)

        if x_test.size != 0:
            y_test_pred = layers[0].predict(x_test)
            loss_test = self.loss_function.get(y=y_test_pred, t=y_test)

        if not isinstance(self.loss_function, SquaredError):
            acc_train = self.__get_accuracy(y=y_train, y_pred=y_train_pred)

            if y_test_pred.size != 0:
                acc_test = self.__get_accuracy(y=y_test, y_pred=y_test_pred)

        if self.lc is not None:
            self.lc.add(loss_train, loss_test, acc_train, acc_test)
            self.lc.stdout(epoch)

    def __get_accuracy(self, y, y_pred):
        """Calculate accuracy and return it.

        Arguments
        ---------
        y : np.array
            Reference of target features in 2d array.
            y.shape == (num of data, num of feature)
        y_pred : np.array
            Predicted target features in 2d array.
            y_pred.shape == (num of data, num of feature)

        Returns
        -------
        float
            Accuracy of predicted result in range from 0.0 to 1.0.

        Warning
        -------
            This method is supposed to be called in the case of classification.
        """
        consistency = np.argmax(y, axis=1) == np.argmax(y_pred, axis=1)
        return consistency.sum().astype(self.dtype) / consistency.shape[0]

