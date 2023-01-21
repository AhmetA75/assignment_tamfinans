First of all for generally analyzing our dataset i used Sweetviz from AutoEda-Tools. Sweetviz basically makes visualizations for us after
 i received visializations. i made preporcessing on our dataset,for handling NAN and empty spaces in datased i applied KNNImputater.
 I sperated categoric datas from dataset and i made encoding for it with One-Hot-Encoder. After that i detected our target column according to our dataset's condition.
 About correlations with target column, i found four column the highest correlation with target and i continue processing with them.In ML procedures i used three different ml algorithms GaussianNB,Random Forest, Decision Tree. According to score metric i choosed Gaussian NB for gird search and so on. After grid search i made classification report, confusion matrix as a result.
 For visualizations i applied clustering and PCA(Dimensionality reduction) as a final visualisations i used shap for detailed illustrations
 
