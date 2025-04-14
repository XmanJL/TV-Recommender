from model import RecommenderModel
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx import to_onnx

if __name__ == "__main__":
    model = RecommenderModel()
    knn = model.content_knn

    initial_type = [("float_input", FloatTensorType([None, knn.n_features_in_]))]
    onnx_model = to_onnx(knn, initial_types=initial_type)

    with open("model/model.onnx", "wb") as f:
        f.write(onnx_model.SerializeToString())