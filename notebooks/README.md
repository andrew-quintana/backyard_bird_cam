# MobileNetV2 Transfer Learning and Fine-Tuning on Google Colab

This notebook implements transfer learning and fine-tuning using the MobileNetV2 architecture on Google Colab. It is designed for image classification tasks and allows for future retraining when new classes are added.

## Features
- **Transfer Learning**: Utilizes the pre-trained MobileNetV2 model (on ImageNet) as a feature extractor.
- **Fine-Tuning**: Allows unfreezing and retraining specific layers of the MobileNetV2 model for task-specific adjustments.
- **Data Augmentation**: Includes optional augmentation techniques to enhance model generalization.
- **Evaluation**: Provides performance metrics such as accuracy, loss, classification report, and confusion matrix.
- **Visualization**: Heatmap of the confusion matrix and example predictions.

## Prerequisites
1. A Google account with access to [Google Colab](https://colab.research.google.com/).
2. A dataset organized in the following directory structure:
…
dataset/
train/
class_1/
class_2/
…
validation/
class_1/
class_2/
…
test/
class_1/
class_2/
…

3. Install required Python packages (most are pre-installed in Colab):
```bash
!pip install seaborn

Steps in the Notebook
	1.	Load and Preprocess Data:
	•	Uses ImageDataGenerator to load and preprocess training, validation, and test datasets.
	2.	Build the Model:
	•	Creates a transfer learning model with MobileNetV2.
	3.	Train the Model:
	•	Initial training with frozen MobileNetV2 base.
	•	Fine-tuning by unfreezing specific layers for further optimization.
	4.	Evaluate the Model:
	•	Computes test accuracy, loss, and classification report.
	•	Visualizes the confusion matrix as a heatmap.
	5.	Future Retraining:
	•	Prepares the model for retraining with additional classes as needed.

How to Use
	1.	Upload this notebook to Google Colab.
	2.	Upload your dataset to your Colab runtime or mount Google Drive to access it:

from google.colab import drive
drive.mount('/content/drive')


	3.	Update the dataset paths in the notebook to point to your dataset directories.
	4.	Run all cells sequentially to train, fine-tune, and evaluate the model.
	5.	Save the trained model for future use:

model.save('mobilenet_v2_best_model.h5')



Output
	•	Model Checkpoint: The trained model is saved for deployment or further training.
	•	Performance Metrics: Training/validation accuracy and loss curves, test accuracy, and confusion matrix.

Notes
	•	Ensure your dataset fits into Colab’s memory limits. If necessary, reduce the input image size or batch size.
	•	For best results, use a GPU runtime in Colab:
	•	Go to Runtime > Change runtime type > Select GPU.

Happy training!

