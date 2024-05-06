import re
from typing import TYPE_CHECKING

import pytest
import torch
from safeds.data.image.containers import ImageList
from safeds.data.labeled.containers import ImageDataset
from safeds.data.tabular.containers import Column, Table
from safeds.data.tabular.transformation import OneHotEncoder
from safeds.ml.nn import (
    AvgPooling2DLayer,
    Convolutional2DLayer,
    ConvolutionalTranspose2DLayer,
    FlattenLayer,
    ForwardLayer,
    InputConversionImage,
    MaxPooling2DLayer,
    NeuralNetworkClassifier,
    NeuralNetworkRegressor,
    OutputConversionImageToTable,
)
from safeds.ml.nn._output_conversion_image import OutputConversionImageToColumn, OutputConversionImageToImage
from syrupy import SnapshotAssertion
from torch.types import Device

from tests.helpers import device_cpu, device_cuda, images_all, resolve_resource_path, skip_if_device_not_available

if TYPE_CHECKING:
    from safeds.ml.nn import Layer


class TestImageToTableClassifier:

    @pytest.mark.parametrize(
        ("seed", "device", "layer_3_bias", "prediction_label"),
        [
            (
                1234,
                device_cuda,
                [0.5809096097946167, -0.32418742775917053, 0.026058292016386986, 0.5801554918289185],
                ["grayscale"] * 7,
            ),
            (
                4711,
                device_cuda,
                [-0.8114155530929565, -0.9443624019622803, 0.8557258248329163, -0.848240852355957],
                ["white_square"] * 7,
            ),
            (
                1234,
                device_cpu,
                [-0.6926110982894897, 0.33004942536354065, -0.32962560653686523, 0.5768553614616394],
                ["grayscale"] * 7,
            ),
            (
                4711,
                device_cpu,
                [-0.9051575660705566, -0.8625037670135498, 0.24682046473026276, -0.2612163722515106],
                ["white_square"] * 7,
            ),
        ],
        ids=["seed-1234-cuda", "seed-4711-cuda", "seed-1234-cpu", "seed-4711-cpu"],
    )
    def test_should_train_and_predict_model(
        self,
        seed: int,
        layer_3_bias: list[float],
        prediction_label: list[str],
        device: Device,
    ) -> None:
        skip_if_device_not_available(device)
        torch.set_default_device(device)
        torch.manual_seed(seed)

        image_list, filenames = ImageList.from_files(resolve_resource_path(images_all()), return_filenames=True)
        image_list = image_list.resize(20, 20)
        classes = []
        for filename in filenames:
            groups = re.search(r"(.*)[\\/](.*)\.", filename)
            if groups is not None:
                classes.append(groups.group(2))
        image_classes = Table({"class": classes})
        one_hot_encoder = OneHotEncoder().fit(image_classes, ["class"])
        image_classes_one_hot_encoded = one_hot_encoder.transform(image_classes)
        image_dataset = ImageDataset(image_list, image_classes_one_hot_encoded)
        num_of_classes: int = image_dataset.output_size if isinstance(image_dataset.output_size, int) else 0
        layers = [Convolutional2DLayer(1, 2), MaxPooling2DLayer(10), FlattenLayer(), ForwardLayer(num_of_classes)]
        nn_original = NeuralNetworkClassifier(
            InputConversionImage(image_dataset.input_size),
            layers,
            OutputConversionImageToTable(),
        )
        nn = nn_original.fit(image_dataset, epoch_size=2)
        assert str(nn_original._model.state_dict().values()) != str(nn._model.state_dict().values())
        assert nn._model.state_dict()["_pytorch_layers.3._layer.bias"].tolist() == layer_3_bias
        prediction: ImageDataset = nn.predict(image_dataset.get_input())
        assert one_hot_encoder.inverse_transform(prediction.get_output()) == Table({"class": prediction_label})


class TestImageToColumnClassifier:

    @pytest.mark.parametrize(
        ("seed", "device", "layer_3_bias", "prediction_label"),
        [
            (
                1234,
                device_cuda,
                [0.5805736780166626, -0.32432740926742554, 0.02629312314093113, 0.5803964138031006],
                ["grayscale"] * 7,
            ),
            (
                4711,
                device_cuda,
                [-0.8114045262336731, -0.9443488717079163, 0.8557113409042358, -0.8482510447502136],
                ["white_square"] * 7,
            ),
            (
                1234,
                device_cpu,
                [-0.69260174036026, 0.33002084493637085, -0.32964015007019043, 0.5768893957138062],
                ["grayscale"] * 7,
            ),
            (
                4711,
                device_cpu,
                [-0.9051562547683716, -0.8625034093856812, 0.24682027101516724, -0.26121777296066284],
                ["white_square"] * 7,
            ),
        ],
        ids=["seed-1234-cuda", "seed-4711-cuda", "seed-1234-cpu", "seed-4711-cpu"],
    )
    def test_should_train_and_predict_model(
        self,
        seed: int,
        layer_3_bias: list[float],
        prediction_label: list[str],
        device: Device,
    ) -> None:
        skip_if_device_not_available(device)
        torch.set_default_device(device)
        torch.manual_seed(seed)

        image_list, filenames = ImageList.from_files(resolve_resource_path(images_all()), return_filenames=True)
        image_list = image_list.resize(20, 20)
        classes = []
        for filename in filenames:
            groups = re.search(r"(.*)[\\/](.*)\.", filename)
            if groups is not None:
                classes.append(groups.group(2))
        image_classes = Column("class", classes)
        image_dataset = ImageDataset(image_list, image_classes, shuffle=True)
        num_of_classes: int = image_dataset.output_size if isinstance(image_dataset.output_size, int) else 0

        layers = [Convolutional2DLayer(1, 2), AvgPooling2DLayer(10), FlattenLayer(), ForwardLayer(num_of_classes)]
        nn_original = NeuralNetworkClassifier(
            InputConversionImage(image_dataset.input_size),
            layers,
            OutputConversionImageToColumn(),
        )
        nn = nn_original.fit(image_dataset, epoch_size=2)
        assert str(nn_original._model.state_dict().values()) != str(nn._model.state_dict().values())
        assert nn._model.state_dict()["_pytorch_layers.3._layer.bias"].tolist() == layer_3_bias
        prediction: ImageDataset = nn.predict(image_dataset.get_input())
        assert prediction.get_output() == Column("class", prediction_label)


class TestImageToImageRegressor:

    @pytest.mark.parametrize(
        ("seed", "device", "layer_3_bias"),
        [
            (1234, device_cuda, [0.13570494949817657, 0.02420804090797901, -0.1311846673488617, 0.22676928341388702]),
            (4711, device_cuda, [0.11234158277511597, 0.13972002267837524, -0.07925988733768463, 0.07342307269573212]),
            (1234, device_cpu, [-0.1637762188911438, 0.02012808807194233, -0.22295698523521423, 0.1689515858888626]),
            (4711, device_cpu, [-0.030541712418198586, -0.15364733338356018, 0.1741572618484497, 0.015837203711271286]),
        ],
        ids=["seed-1234-cuda", "seed-4711-cuda", "seed-1234-cpu", "seed-4711-cpu"],
    )
    def test_should_train_and_predict_model(
        self,
        seed: int,
        snapshot_png_image_list: SnapshotAssertion,
        layer_3_bias: list[float],
        device: Device,
    ) -> None:
        skip_if_device_not_available(device)
        torch.set_default_device(device)
        torch.manual_seed(seed)

        image_list = ImageList.from_files(resolve_resource_path(images_all()))
        image_list = image_list.resize(20, 20)
        image_list_grayscale = image_list.convert_to_grayscale()
        image_dataset = ImageDataset(image_list, image_list_grayscale)

        layers: list[Layer] = [
            Convolutional2DLayer(6, 2),
            Convolutional2DLayer(12, 2),
            ConvolutionalTranspose2DLayer(6, 2),
            ConvolutionalTranspose2DLayer(4, 2),
        ]
        nn_original = NeuralNetworkRegressor(
            InputConversionImage(image_dataset.input_size),
            layers,
            OutputConversionImageToImage(),
        )
        nn = nn_original.fit(image_dataset, epoch_size=20)
        assert str(nn_original._model.state_dict().values()) != str(nn._model.state_dict().values())
        assert nn._model.state_dict()["_pytorch_layers.3._layer.bias"].tolist() == layer_3_bias
        prediction: ImageDataset = nn.predict(image_dataset.get_input())
        assert prediction.get_output() == snapshot_png_image_list