# **Real-time Crime Rate Prediction System**


This is a project that aims to predict crime rates in real-time using machine learning algorithms and data from different sources, including [San Francisco government data](https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783), [weather data](https://dev.meteostat.net/python/), and [basketball schedule data](https://www.basketball-reference.com/). The project also includes a CI/CD pipeline to automate the data processing, model training, and deployment.


![embed](https://github.com/pjeena/Real-time-crime-rate-detection-using-CI-CD/blob/main/architecture.jpeg)


## **Data Collection**
The project collects data from the following APIs:

[San Francisco government data API](https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783): provides information about crime incidents, including the type of crime, the location, and the time of the incident.

[Weather API](https://dev.meteostat.net/python/): provides information about weather conditions in San Francisco, including temperature, humidity, wind speed, and precipitation.

[Basketball schedule](https://www.basketball-reference.com/): provides information about NBA games that take place in San Francisco, including the date, time, and location of the games.

The collected data is then preprocessed and inserted into [MongoDB](https://www.mongodb.com/), a document-oriented database that stores the data in a parquet format since its more efficient data format for bigger files. 



## **Preprocessing**

Before building the machine learning model, the collected data is preprocessed to clean and transform it into a suitable format. The following preprocessing steps are performed:

**Data cleaning**: remove duplicate entries, filled missing values, and correct erroneous data.

**Feature engineering**: create new features based on the existing data, such as time of day, day of the week, and season.

**Feature selection**: select the most relevant features using techniques correlation analysis and feature importance ranking.


## Model Building

After getting the data in the appropriate format, several models(Linear regression, Random forest, Gradient boosting algorithms) were tried on historical data with hyper parameter tuning and evaluated using R2 score. The best model came out to be Xgboost with around 85% accuracy. Therefore, it was used for real time prediction. 

## CI/CD Pipeline

To automate data fetching, data processing, model training, and deployment, a CI/CD pipeline is implemented using Github actions. The pipeline includes the following stages:

**Data collection**: collect data from the APIs and insert it into MongoDB.

**Preprocessing**: preprocess the collected data and prepare it for machine learning.

**Model training**: train the machine learning model on historical data.

**Model evaluation**: evaluate the performance of the model using metrics such as accuracy, precision, recall, and F1 score.

**Model deployment**: deploy the model on a [web-based dashboard](https://pjeena-real-time-crime-rate-detection-using-ci-cd-app-knxaip.streamlit.app/), which displays real-time crime rate predictions.


The pipeline is triggered automatically whenever new data is available, ensuring that the model is always up-to-date and accurate.

## Dashboard

The predicted data was visualized by projecting it to a folium map(https://pjeena-real-time-crime-rate-detection-using-ci-cd-app-knxaip.streamlit.app/) showing the predicted number of crimes in each district of San Francisco. 


## Conclusion

This project demonstrates how machine learning algorithms can be used to predict crime rates in real-time, using data from different sources. The project also shows how a CI/CD pipeline can be implemented to automate the data processing, model training, and deployment, improving the efficiency and reliability of the project.

## Future work

This project provides a foundation for further development and improvement. Some possible areas for future work include:

**Integration with additional data sources** : incorporating data from other sources, such as social media feeds or traffic cameras.

**User feedback and interaction**: gathering user feedback and incorporating it into the design and functionality of the dashboard could improve its usability and usefulness for the public and law enforcement agencies.

Overall, I really enjoyed working on this end to end project. I enjoyed the challenge of collecting and preprocessing data from multiple sources and building a machine learning model to predict crime rates in real-time. The implementation of the CI/CD pipeline was a great learning experience for me as well, and I am proud of the automation and efficiency it brought to the project. Overall, I feel like I grew as a data scientist.

