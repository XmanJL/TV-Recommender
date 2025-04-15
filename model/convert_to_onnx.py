from model import RecommenderModel
"""Convert a trained KNN model to ONNX format.

This script converts a trained K-Nearest Neighbors model from the RecommenderModel
class to ONNX format for deployment. The converted model is saved to 'model/model.onnx'.

The ONNX model expects input features in the same format as the original KNN model
(float tensor with shape [None, n_features]).

Requirements:
    - skl2onnx
    - The trained RecommenderModel must be available

Returns:
    None. The converted model is saved to disk as 'model/model.onnx'.
"""
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx import to_onnx

if __name__ == "__main__":
    model = RecommenderModel()
    knn = model.content_knn

    initial_type = [("float_input", FloatTensorType([None, knn.n_features_in_]))]
    onnx_model = to_onnx(knn, initial_types=initial_type)

    with open("model/model.onnx", "wb") as f:
        f.write(onnx_model.SerializeToString())