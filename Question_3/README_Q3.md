## Question_1

First of all, for generally analyzing our dataset **Sweetviz** from AutoEda-Tools was used.
Sweetviz basically analyzes the dataset and makes visualizations.

After analyzing and visualization of the data completed, preprocessing on the dataset completed.

For handling NAN and empty spaces in dataset, **KNN Imputater** was applied.
Categorical data seperated from dataset and encoding was applied for it with **One-Hot-Encoder**.

After that target column was detected according to the dataset's condition.
About correlations with target column, four column was found the highest correlation with target and processed with them.

In *Machine Learning* procedures, three different ML algorithms was used: *GaussianNB*, *Random Forest* and *Decision Tree*.
According to the score metric Gaussian NB was chosen for grid search and so on.
After grid search classification report and confusion matrix was prepared.

For clustering **PCA(Dimensionality reduction)** and **KMeans** was used.
As a final visualisations **Shap** was used for detailed illustrations.
