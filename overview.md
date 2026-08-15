# 🧬 Drug-Drug Interaction Prediction using Graph Neural Networks

## 📌 About the Project

This project predicts potential drug-drug interactions using
Graph Neural Networks (GNNs).

The system analyzes molecular features of drugs and predicts
whether two drugs may interact. It also classifies the
interaction risk level as Low, Medium, or High.

## 🎯 Objectives

- Predict potential drug-drug interactions
- Extract molecular and graph-based features
- Use Graph Attention Networks for learning
- Classify interaction risk
- Provide an easy-to-use prediction interface

## 🛠️ Technologies Used

- Python
- PyTorch
- PyTorch Geometric
- RDKit
- Pandas
- NumPy
- Scikit-learn
- Streamlit

## 🧠 Model Architecture

Drug Input
↓
SMILES Processing
↓
Molecular Feature Extraction
↓
Graph Representation
↓
Graph Attention Network (GAT)
↓
Node Embeddings
↓
Link Prediction
↓
Interaction Probability
↓
Risk Classification

## 📊 Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC
- Confusion Matrix

## 🚀 Installation

```bash
git clone YOUR_REPOSITORY_URL
cd drug-drug-interaction-prediction
pip install -r requirements.txt
