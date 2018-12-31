# import libraries needed for the code to run
import re
import pyspark as ps
from pyspark.ml import PipelineModel
from pyspark.sql import functions as f
from pyspark.sql import types as t
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

#define regex pattern for preprocessing
pat1 = r'@[A-Za-z0-9_]+'
pat2 = r'https?://[^ ]+'
combined_pat = r'|'.join((pat1,pat2))
www_pat = r'www.[^ ]+'
negations_dic = {"isn't":"is not", "aren't":"are not", "wasn't":"was not", "weren't":"were not",
                "haven't":"have not","hasn't":"has not","hadn't":"had not","won't":"will not",
                "wouldn't":"would not", "don't":"do not", "doesn't":"does not","didn't":"did not",
                "can't":"can not","couldn't":"could not","shouldn't":"should not","mightn't":"might not",
                "mustn't":"must not"}
neg_pattern = re.compile(r'\b(' + '|'.join(negations_dic.keys()) + r')\b')

# preprocessing for
# first_process: to remove Twitter handle and URL
# second_process: to remove URL pattern starting with www.
# third_process: to lower characters
# fourth_process: to replace contracted negation with proper forms
# result: remove numbers and special characters
def pre_processing(column):
    first_process = re.sub(combined_pat, '', column)
    second_process = re.sub(www_pat, '', first_process)
    third_process = second_process.lower()
    fourth_process = neg_pattern.sub(lambda x: negations_dic[x.group()], third_process)
    result = re.sub(r'[^A-Za-z ]','',fourth_process)
    return result.strip()

# create a Flask instance
# and create a Flask-RESTful API instance with the created Flask instance
app = Flask(__name__)
api = Api(app)

# create a SparkContext
# load saved pipeline model from the folder 'model'
sc = ps.SparkContext()
sqlContext = ps.sql.SQLContext(sc)
loadedModel = PipelineModel.load('model')

# create a parser
# fill a parser with information about arguments 
parser = reqparse.RequestParser()
parser.add_argument('query')


class PredictSentiment(Resource):
    def get(self):
        # retrieve query text from API call
        args = parser.parse_args()
        user_text = args['query']
        # create a dictionary with the retrieved query text
        # and make a PySpark dataframe 
        user_input = {'text':user_text}
        schema = t.StructType([t.StructField('text', t.StringType())])
        df=sqlContext.createDataFrame([user_input],schema)
        # make a user defined function from the above defined pre_processing function
        # apply to dataframe so that the processed text will be stored under 'tweet' column
        reg_replaceUdf = f.udf(pre_processing, t.StringType())
        df = df.withColumn('tweet', reg_replaceUdf(f.col('text')))
        # predict sentiment with loaded PySpark ML model
        prediction = loadedModel.transform(df)
        # retrieve predicted label ('prediction' column):
        #       trained model will output 0 for negative sentiment and 1 for positive sentiment
        prediction_label = prediction.select(prediction['prediction']).collect()
        # retrieve prediction probability:
        #       it will be an array with two probabilities,
        #       the first number is the probability of the text to be negative sentiment
        #       the second number is the probability of the text to be positive sentiment
        probability = prediction.select(prediction['probability']).collect()
        # store predicted label as integer to a variable 'sentiment'
        sentiment = int([r['prediction'] for r in prediction_label][0])
        # store the higher probability of the two labels (rounded to 3 decimals) to a variable 'confidence'
        confidence = round(max([r['probability'] for r in probability][0]),3)
        # finally make a dictionary with 'sentiment' and 'confidence'
        output = {'sentiment':sentiment, 'confidence':confidence}
        # return the dictionary
        return output


# Setup the Api resource routing
# Route the URL to the resource
api.add_resource(PredictSentiment, '/')


if __name__ == '__main__':
    # run the Flask RESTful API, make the server publicly available (host='0.0.0.0') on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
