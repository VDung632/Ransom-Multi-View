import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt
import os
import sys

def select_features(X_Data, Y_Data, max_features_to_display=22):
    """
    Performs feature selection using Extra Trees Classifier.

    Args:
        X_Data (pd.DataFrame): Input features.
        Y_Data (pd.DataFrame): Target labels.
        max_features_to_display (int): Maximum number of features to display in the plot.

    Returns:
        pd.DataFrame: Selected features.
        list: Indices of the selected features.
        list: Names of the selected features.
    """
    print("Feature Selection")
    model = ExtraTreesClassifier(n_estimators=500, random_state=0, n_jobs=1,
                                    max_depth=25)
    model.fit(X_Data, Y_Data.values.ravel())
    importances = model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in model.estimators_],
                    axis=0)
    indices = np.argsort(importances)[::-1]

    print("Feature ranking:")
    selected_features_indices = []
    selected_features_importances = []
    for f in range(X_Data.shape[1]):
        if importances[indices[f]] > 0.000001:
            selected_features_indices.append(indices[f])
            print(f"{f + 1}. Feature {indices[f]} ({importances[indices[f]]})")
            selected_features_importances.append(importances[indices[f]])

    print(len(selected_features_indices), selected_features_indices)

    # Store feature names of selected features
    selected_feature_names = X_Data.columns[
        selected_features_indices].tolist()

    X_Data_Selected = X_Data.iloc[:, selected_features_indices]

    # Visualize feature importances
    num_features_to_display = min(len(selected_features_indices),
                                    max_features_to_display)
    plt.figure()
    plt.title("Feature importances")
    plt.bar(range(num_features_to_display),
            selected_features_importances[:num_features_to_display],
            color="r",
            yerr=std[selected_features_indices[:num_features_to_display]],
            align="center")
    plt.xticks(range(num_features_to_display),
                selected_features_indices[:num_features_to_display])
    plt.xlim([-1, num_features_to_display])
    plt.ylabel('Importance')
    plt.xlabel('Feature index')
    plt.show()

    return X_Data_Selected, selected_features_indices, selected_feature_names

def main():
    print("Python main function")
    # Get the CSV file path from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python featureselect.py <input_csv_path>")
        sys.exit(1)
    csv_file_path = sys.argv[1]

    # Read the CSV file
    Train = pd.read_csv(csv_file_path, skip_blank_lines=True)

    # Separate the first 13 columns (APK name + 12 information columns)
    initial_columns = Train.iloc[:, :13]
    features = Train.iloc[:, 13:-1]
    labels = Train.iloc[:, -1]

    # Perform feature selection
    X_Data_Selected, selected_features_indices, selected_feature_names = select_features(
        features, labels)

    # Combine the initial columns with the selected features
    X_Data_Selected_with_initial = pd.concat([initial_columns, X_Data_Selected],
                                                axis=1)
    X_Data_Selected_with_initial_and_label = pd.concat(
        [X_Data_Selected_with_initial, labels.reset_index(drop=True)], axis=1)

    # Update headers to reflect selected features
    X_Data_Selected_with_initial_and_label.columns = list(
        initial_columns.columns) + selected_feature_names + ['Label']

    # Save the resulting dataset to a new CSV file
    output_csv_path = "Selected_Features.csv"
    X_Data_Selected_with_initial_and_label.to_csv(output_csv_path, index=False,
                                                    header=True)

    print(
        f"Selected features saved to '{output_csv_path}' with shape: {X_Data_Selected_with_initial.shape}")

if __name__ == "__main__":
    main()