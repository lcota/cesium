from mltsp import build_model
from mltsp import cfg
from nose.tools import with_setup
import os
from os.path import join as pjoin
from sklearn.externals import joblib
import shutil
import xarray as xr


DATA_PATH = pjoin(os.path.dirname(__file__), "data")


def copy_classification_test_data():
    fnames = ["test_featureset.nc", "test_featureset_10.nc"]
    for fname in fnames:
        shutil.copy(pjoin(DATA_PATH, fname), cfg.FEATURES_FOLDER)


def copy_regression_test_data():
    fnames = ["test_reg_featureset.nc"]
    for fname in fnames:
        shutil.copy(pjoin(DATA_PATH, fname), cfg.FEATURES_FOLDER)


def remove_test_data():
    fnames = ["test_featureset.nc", "test_featureset_10.nc",
              "test_reg_featureset.nc", "test.pkl"]
    for fname in fnames:
        for data_dir in [cfg.FEATURES_FOLDER, cfg.MODELS_FOLDER]:
            try:
                os.remove(pjoin(data_dir, fname))
            except OSError:
                pass


@with_setup(copy_classification_test_data, remove_test_data)
def test_build_model_rfc():
    """Test main model building method - Random Forest Classifier"""
    build_model.create_and_pickle_model("test", "Random Forest Classifier",
                                        "test")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict_proba")
    assert "sklearn.ensemble.forest.RandomForestClassifier" in str(type(model))


@with_setup(copy_regression_test_data, remove_test_data)
def test_build_model_rfr():
    """Test main model building method - Random Forest Regressor"""
    build_model.create_and_pickle_model("test", "Random Forest Regressor",
                                        "test_reg")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict")
    assert "sklearn.ensemble.forest.RandomForestRegressor" in str(type(model))


@with_setup(copy_classification_test_data, remove_test_data)
def test_build_model_lin_class():
    """Test main model building method - linear classifier"""
    build_model.create_and_pickle_model("test", "Linear SGD Classifier", "test")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict")
    assert "SGDClassifier" in str(type(model))


@with_setup(copy_regression_test_data, remove_test_data)
def test_build_model_lin_reg():
    """Test main model building method - linear regressor"""
    build_model.create_and_pickle_model("test", "Linear Regressor", "test_reg")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict")
    assert "LinearRegression" in str(type(model))


@with_setup(copy_classification_test_data, remove_test_data)
def test_build_model_ridge_cv():
    """Test main model building method - Ridge Classifer CV"""
    build_model.create_and_pickle_model("test", "Ridge Classifier CV", "test")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict")
    assert "RidgeClassifierCV" in str(type(model))


@with_setup(copy_regression_test_data, remove_test_data)
def test_build_model_ard_reg():
    """Test main model building method - ARD Regression"""
    build_model.create_and_pickle_model("test", "Bayesian ARD Regressor",
                                        "test_reg")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict")
    assert "ARDRegression" in str(type(model))


@with_setup(copy_regression_test_data, remove_test_data)
def test_build_model_ard_reg():
    """Test main model building method - Bayesian Ridge Regression"""
    build_model.create_and_pickle_model("test", "Bayesian Ridge Regressor",
                                        "test_reg")
    model = joblib.load(pjoin(cfg.MODELS_FOLDER, "test.pkl"))
    assert hasattr(model, "predict")
    assert "BayesianRidge" in str(type(model))


@with_setup(copy_classification_test_data, remove_test_data)
def test_fit_existing_model():
    """Test model building helper function."""
    featureset = xr.open_dataset(pjoin(cfg.FEATURES_FOLDER,
                                         "test_featureset.nc"))
    model = build_model.MODELS_TYPE_DICT['Random Forest Classifier']()
    model = build_model.build_model_from_featureset(featureset, model)
    assert hasattr(model, "n_features_")
    assert hasattr(model, "predict_proba")
    assert "sklearn.ensemble.forest.RandomForestClassifier" in str(type(model))


@with_setup(copy_classification_test_data, remove_test_data)
def test_fit_existing_model_optimize():
    """Test model building helper function - with param. optimization"""
    featureset = xray.open_dataset(pjoin(cfg.FEATURES_FOLDER,
                                         "test_featureset_10.nc"))
    model = build_model.MODELS_TYPE_DICT['Random Forest Classifier']()
    model_options = {"n_estimators": [10, 50, 100, 1000], "criterion": "gini",
                     "min_samples_split": [2, 5],
                     "max_features": ["auto", 3], "bootstrap": True}
    params_to_optimize = ["n_estimators", "min_samples_split", "max_features"]
    model = build_model.build_model_from_featureset(
        featureset, model=model, model_options=model_options,
        params_to_optimize=params_to_optimize)
    assert hasattr(model, "best_params_")
    assert hasattr(model, "predict_proba")
    assert "sklearn.grid_search.GridSearchCV" in str(type(model))


@with_setup(copy_classification_test_data, remove_test_data)
def test_fit_optimize():
    """Test hypeparameter optimization"""
    featureset = xray.open_dataset(pjoin(cfg.FEATURES_FOLDER,
                                         "test_featureset_10.nc"))
    model = build_model.MODELS_TYPE_DICT['Random Forest Classifier']()
    feature_df = build_model.rectangularize_featureset(featureset)
    model_options = {"n_estimators": [10, 50, 100, 1000], "criterion": "gini",
                     "min_samples_split": [2, 5],
                     "max_features": ["auto", 3], "bootstrap": True}
    params_to_optimize = ["n_estimators", "min_samples_split", "max_features"]
    model = build_model.fit_model_optimize_hyperparams(
        feature_df, featureset['target'], model, model_options,
        params_to_optimize)
    assert hasattr(model, "best_params_")
    assert hasattr(model, "predict_proba")
    assert "sklearn.grid_search.GridSearchCV" in str(type(model))
